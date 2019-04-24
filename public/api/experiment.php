<?php
class Experiment extends API {
    public function get($id, $params) {
        try {
            $where = array();
            $filter = array();
            $tokens = array();
            $sql = "SELECT e.`id` AS `experiment_id`, e.`name`, "
                 ."f.`id` AS `field_id`, f.`title` AS `field_title`, f.`weight`, "
                 ."CONCAT_WS('-',ef.`value_INT`,ef.`value_VARCHAR`,ef.`value_DOUBLE`,ef.`value_BOOL`,ef.`value_TEXT`) AS `value` "
                 ."FROM `experiments` e "
                 ."LEFT JOIN `experiments_fields` ef ON e.`id` = ef.`experiment_id` "
                 ."LEFT JOIN `fields` f ON ef.`field_id` = f.`id` ";

            $filter_b = "e.`id` IN (SELECT ef_filter.`experiment_id` "
                      ."FROM `experiments_fields` ef_filter "
                      ."WHERE ";
            $filter_e = ") ";
            
            $order = " ORDER BY e.`id`, f.`weight`";

            //map all field types
            $fields_sql = "SELECT `id`, `type_column` FROM `fields`";
            $qry = $this->db->prepare($fields_sql);
            $qry->setFetchMode(PDO::FETCH_ASSOC);
            $qry->execute();
            $res = $qry->fetchAll();
            $field_types = array();
            foreach ($res as $row){
                $field_types[$row['id']] = explode('_', $row['type_column'])[1];
            }
            
            //fetch all fields/values for the experiments
            if (empty($id)) {
                if (isset($params['ExperimentName'])){
                    $where[] = "e.`name` like CONCAT('%', :ExperimentName ,'%') ";
                    $tokens[':ExperimentName'] = $params['ExperimentName'];
                }
                
                foreach($params as $key => $value){
                    $key_parts = explode('_', $key);
                    if (count($key_parts) == 2){
                        $field_id = $key_parts[1];                        
                    } else {
                        $field_id = $key;
                    }
                    $field_type = $field_types[$field_id];

                    switch($field_type){
                    case 'VARCHAR':
                    case 'TEXT':
                        $filter_query = "(ef_filter.`field_id` = :FieldID_$field_id AND ef_filter.`value_$field_type` like CONCAT('%', :FieldValue_$field_id ,'%')) ";
                        $tokens[":FieldID_$field_id"] = $field_id;
                        $tokens[":FieldValue_$field_id"] = $value;
                        $where[] = $filter_b . $filter_query . $filter_e;
                        break;
                    case 'INT':
                    case 'DOUBLE':
                        $filter_query = "(ef_filter.`field_id` = :FieldID_$field_id ";
                        $tokens[":FieldID_$field_id"] = $field_id;                        
                        if (isset($params['min_'.$field_id])){
                            $min_value = $params['min_'.$field_id];
                            $filter_query.= "AND ef_filter.`value_$field_type` >= :FieldMinValue_$field_id ";
                            $tokens[":FieldMinValue_$field_id"] = $min_value;
                        }                            
                        if (isset($params['max_'.$field_id])){
                            $max_value = $params['max_'.$field_id];
                            $filter_query.= "AND ef_filter.`value_$field_type` <= :FieldMaxValue_$field_id ";
                            $tokens[":FieldMaxValue_$field_id"] = $max_value;
                        }
                        $filter_query.= ") ";
                        $where[] = $filter_b . $filter_query . $filter_e;
                        break;
                    case 'BOOL':
                        $bool_value = $value=='true'? 1:0;
                        $filter_query = "(ef_filter.`field_id` = :FieldID_$field_id "
                                      ."AND ef_filter.`value_BOOL` = :FieldValue_$field_id) ";
                        $tokens[":FieldID_$field_id"] = $field_id;
                        $tokens[":FieldValue_$field_id"] = $bool_value;
                        $where[] = $filter_b . $filter_query . $filter_e;
                        break;
                    }
                }
                if (count($where) > 0){                    
                    $sql.=" WHERE ".implode(" AND ", $where);
                }
                $sql.= $order;
                error_log($sql);
                $qry = $this->db->prepare($sql);
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute($tokens);
                $res = $qry->fetchAll();                
            } else {
                $where[]= " e.`id` = :ID";
                $tokens[':ID'] = $id;

                $sql.=" WHERE ".implode(" AND ", $where);
                $qry = $this->db->prepare($sql);
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute($tokens);
                $res = $qry->fetchAll();
            }

            //gather fields/values per experiment in an assoc array
            $summary = array();
            foreach ($res as $entry){
                $experiment_id = $entry['experiment_id'];
                if (!isset($summary[$experiment_id])){
                    $summary[$experiment_id] = array();
                    $summary[$experiment_id]['name'] = $entry['name'];
                    $summary[$experiment_id]['fields'] = array();
                }

                $field_id = $entry['field_id'];
                $field_value = $entry['value'];
                if (!isset($summary[$experiment_id]['fields'][$field_id])){
                    $summary[$experiment_id]['fields'][$field_id] = array();
                }
                $summary[$experiment_id]['fields'][$field_id][] = $field_value;
            }

            //generate a list from gathered results and add the references and species to each entry
            $result = array();
            foreach ($summary as $exp_id => $exp){
                //ID
                $exp['id'] = $exp_id;

                //References
                $sql = "SELECT r.`id`, r.`authors`, r.`title`, r.`journal`, r.`year`, r.`pages`, r.`pubmed_id`, r.`url` "
                     ."FROM `references` r "
                     ."JOIN `experiments_references` er ON r.`id` = er.`reference_id` "
                     ."WHERE er.`experiment_id` = :ID";
                
                $qry = $this->db->prepare($sql);
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute(array(":ID" => $exp_id));
                $res = $qry->fetchAll();
                                
                $exp['references'] = $res;
                
                $result[] = $exp;
            }
            if (!empty($id)){
                $result = $result[0];
            }
            echo json_encode($result, JSON_NUMERIC_CHECK);
        } catch (PDOException $e) {
            echo "Error: ". $e->getMessage();
        }
    }

    public function post($id, $params){
        //TODO: authentication check
        try{
            $params = json_decode(file_get_contents("php://input"));
            if (empty($id)){
                //Insert new experiment
                //non-admin additions get the "suggestion" flag.
            } else {
                //Update existing experiment
                //non-admin updates are stored as new experiment with a "suggestion" flag
                //and a reference to the original experiment.
            }
        } catch (PDOException $e) {
            echo("Error: ".$e->getMessage());
        }
    }
}
