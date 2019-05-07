<?php
require dirname(__FILE__)."/../../config.php";

class API {

    protected $db;
    protected $dbhost           = CONFIG_DB_HOST;
    protected $dbname           = CONFIG_DB_NAME;
    protected $dbuser           = CONFIG_DB_USER;
    protected $dbpasswd         = CONFIG_DB_PASSWORD;

    public function __construct () {
        try {
            $this->db = new PDO("mysql:dbname=".$this->dbname.";host=".$this->dbhost, $this->dbuser, $this->dbpasswd, array(
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8",
            ));
        } catch (PDOException $e) {
            echo "DB connection failed: " . $e->getMessage();
        }
    }

    public function get($id, $params) {
        die('Not implemented');
    }

    public function post($id, $params) {
        die('Not implemented');
    }

    public function put($id, $params) {
        die('Not implemented');
    }

    public function delete($id, $params) {
        echo "1";
    }

}


include "experiment.php";
include "field.php";

$method = $_SERVER['REQUEST_METHOD'];
$params = $_REQUEST;
$API    = isset($_GET['API']) ? $_GET['API'] : '';
$API    = explode("/", $API);
if (!empty($API[0])) {
    $class = ucfirst($API[0]);
    if (class_exists($class)) {
        $class = new $class();
    } else {
        die();
    }
} else {
    $class = new API();
}
$id = isset($API[1]) ? $API[1] : null;
call_user_func_array(array($class, $method), array($id, $params));
