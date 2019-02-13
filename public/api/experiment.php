<?php
class Experiment extends API {

    public function get($id, $params) {
        try {
            if (empty($id)) {
                $qry = $this->db->prepare("SELECT * FROM entries");
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute(array());
                $res = $qry->fetchAll();
            } else {
                $qry = $this->db->prepare("SELECT * FROM entries WHERE experiment_id = :ID");
                $qry->setFetchMode(PDO::FETCH_ASSOC);
                $qry->execute(array(":ID" => $id));
                $res = $qry->fetchAll();
            }
            $summary = array();
            foreach ($res as $entry){
                $experiment_id = $entry['experiment_id'];
                if (!isset($summary[$experiment_id])){
                    $summary[$experiment_id] = array();
                }
                $col_name = $entry['column_name'];
                $col_value = $entry['value'];
                $summary[$experiment_id][$col_name] = $col_value;
            }
            $result = array();
            foreach ($summary as $exp_id => $exp){
                $exp['id'] = $exp_id;
                $result[] = $exp;
            }
            echo json_encode($result, JSON_NUMERIC_CHECK);
        } catch (PDOException $e) {
            echo "Error: ". $e->getMessage();
        }
    }
}
