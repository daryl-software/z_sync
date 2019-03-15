<?php
require_once __DIR__ . '/../../vendor/autoload.php';

$managers = [
    User_Manager_UserHasChannel::class,
    User_Manager_User::class,
    Location_Manager_Location::class,
    User_Manager_Criteria::class,
    User_Manager_AutoLogin::class
];

// try to find dead methods
$class = new ReflectionClass(User_Manager_Criteria::class);
$methods = $class->getMethods();
shuffle($methods);
$n = count($methods);
// todo filter public only
foreach ($methods as $i => $method) {
    $name = $method->name;

    if (strlen($name) > 7) {
        echo '.';

        $cmd = 'ack --php "' . $name . '\(" | grep -v "function ' . $name  . '"';
        $matchs = array_filter(explode(PHP_EOL, trim(shell_exec($cmd))));
        if (!count($matchs)) {
            echo PHP_EOL;
            echo 'processing method ' . $class->getName(). ' ' . $name . ' ' . $i . '/' . $n . PHP_EOL;
            echo '🙃 METHOD NOT FOUND using ' . $cmd . PHP_EOL;
        }
        echo PHP_EOL;
    }
}
