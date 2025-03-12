<?php
$servername = "localhost";
$username = "monitor_user";
$password = "password";
$dbname = "stream_service_monitor";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
