<?php
class Field extends API {
    public function get($id, $params){
        if (empty($id)){
            //Without field id: return the general list of fields
            try {
                $sql = "SELECT `id`, `title`, `unit`, `description`, `type_column`, `options`, `link`, `required`, `weight`, `group`, `group_id` "
                     ."FROM `fields` "
                     ."ORDER BY `weight`";

                $qry = $this->db->prepare($sql);
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute(array());
                $res = $qry->fetchAll();

                echo json_encode($res, JSON_NUMERIC_CHECK);
            } catch (PDOException $e) {
                echo "Error: ". $e->getMessage();
            }
        } else {
            //With given field id: return value stats
            $sql = "SELECT `id`, `title`, `unit`, `type_column` "
                 ."FROM `fields` ";

            $tokens = array();
            if (is_numeric($id)){
                $sql .= "WHERE id = :ID";
                $tokens[':ID'] = $id;
            } else {
                $sql .= "WHERE `title` = :TITLE";
                $tokens[':TITLE'] = $id;
            }
            $qry = $this->db->prepare($sql);
            $qry->setFetchMode(PDO::FETCH_ASSOC);
            $qry->execute($tokens);
            $field_props = $qry->fetch();

            $type_col = $field_props['type_column'];
            if (!isset($params['timeline']) || $params['timeline'] == 0){
                $sql = "SELECT ef.`$type_col` value, COUNT(*) number "
                     ."FROM experiments_fields ef "
                     ."WHERE ef.field_id = :FIELD_ID "
                     ."GROUP BY value "
                     ."ORDER BY number DESC";
            } else {                
                $sql = "SELECT ef.`$type_col` value, r.`year`, COUNT(*) number "
                     ."FROM `experiments_fields` ef "
                     ."JOIN `experiments_references` er ON er.`experiment_id` = ef.`experiment_id` "
                     ."JOIN `references` r ON r.`id` = er.`reference_id` "
                     ."WHERE ef.`field_id` = :FIELD_ID "
                     ."GROUP BY value, year "
                     ."ORDER BY year";
            }
            
            $tokens = array();
            $tokens[':FIELD_ID'] = $field_props['id'];
            $qry = $this->db->prepare($sql);
            $qry->setFetchMode(PDO::FETCH_ASSOC);
            $qry->execute($tokens);
            $field_stats = $qry->fetchAll();

            $field_props['values'] = $field_stats;
            echo json_encode($field_props);

            
        }

    }
}
