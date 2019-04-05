<?php
$config = include __DIR__ . '/config.php';

$action = $_SERVER['argv'][1] ?? null;

foreach ($config['respositories'] as $name => $respository) {
    echo PHP_EOL . '📦 ' . $name . PHP_EOL;
    echo str_repeat('-', 20) . PHP_EOL;

    switch ($action) {
        case 'git-clone':
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

        case 'npm':
            if (!is_file(__DIR__ . '/../' . $name . '/package.json')) {
                echo 'no package.json found' . PHP_EOL;
                break;
            }
            $sub = implode(' ', array_slice($_SERVER['argv'], 2));
            chdir(__DIR__ . '/../' . $name);
            passthru('npm ' . $sub);
            break;

        case 'git-status':
            chdir(__DIR__ . '/../' . $name);

            $output = shell_exec('git status');
            if (strpos($output, 'Changes') || strpos($output, 'diverged') || strpos($output, 'publish your local commits')) {
                echo $output . PHP_EOL;
            } else {
                echo 'no changes' . PHP_EOL;
            }
            break;

        case 'git':
            $sub = implode(' ', array_slice($_SERVER['argv'], 2));
            chdir(__DIR__ . '/../' . $name);
            passthru('git ' . $sub);
            break;

        default:
            throw new \Exception('Unknown action');
    }
}

