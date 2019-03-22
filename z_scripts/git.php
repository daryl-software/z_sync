<?php
$config = include __DIR__ . '/config.php';

$action = $_SERVER['argv'][1] ?? null;

foreach ($config['respositories'] as $name => $respository) {

    echo str_repeat('-', 20) . PHP_EOL;
    echo '   Entering:  ' . $name . PHP_EOL;
    echo str_repeat('-', 20) . PHP_EOL;

    switch ($action) {
        case 'clone':
            passthru('git clone ' . $respository['source'] . ' ' . $name);
            break;

        case 'composer':
            if (!is_file(__DIR__ . '/../' . $name . '/composer.json')) {
                echo 'no composer.json found' . PHP_EOL;
                break;
            }
            $sub = implode(' ', array_slice($_SERVER['argv'], 2));
            chdir(__DIR__ . '/../' . $name);
            passthru('composer ' . $sub);
            break;

        case 'status':
            chdir(__DIR__ . '/../' . $name);

            $output = shell_exec('git status');
            if (strpos($output, 'Changes') || strpos($output, 'diverged') || strpos($output, 'publish your local commits')) {
                echo $output . PHP_EOL;
            } else {
                echo 'no changes' . PHP_EOL;
            }
            break;

        case 'pull':
            chdir(__DIR__ . '/../' . $name);
            passthru('git pull --rebase');
            break;

        default:
            throw new \Exception('Unknown action');
    }
}

