<?php
$config = include __DIR__ . '/config.php';

$action = $_SERVER['argv'][1] ?? null;

foreach ($config['respositories'] as $name => $respository) {
    switch ($action) {
        case 'clone':
            passthru('git clone ' . $respository['source'] . ' ' . $name);
            break;
        case 'deinit':
            echo 'git submodule deinit -f ' . $name . PHP_EOL;
            break;

        case 'status':
            chdir(__DIR__ . '/../' . $name);

            $output = shell_exec('git status');
            if (strpos($output, 'Changes') || strpos($output, 'diverged') || strpos($output, 'publish your local commits')) {
                echo str_repeat('-', 20) . PHP_EOL;
                echo '   ' . $name . PHP_EOL;
                echo str_repeat('-', 20) . PHP_EOL;
                echo $output . PHP_EOL;
            }
            break;

        default:
            throw new \Exception('Unknown action');
    }
}

