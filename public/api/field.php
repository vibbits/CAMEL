<?php
class Field extends API {
    public function get($id, $params){
        try {
            $sql = "SELECT `id`, `title`, `unit`, `type_column`, `options`, `link`, `required`, `column_order` "
                 ."FROM `fields` "
                 ."ORDER BY `column_order`";

            $qry = $this->db->prepare($sql);
            $qry->setFetchMode(PDO::FETCH_ASSOC);
            $qry->execute(array());
            $res = $qry->fetchAll();                

            echo json_encode($res, JSON_NUMERIC_CHECK);
        } catch (PDOException $e) {
            echo "Error: ". $e->getMessage();
        }
    }
}
