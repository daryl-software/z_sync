<?php

$submodules = array_filter(array_map(function($line) {
    $submodule = explode(' ', trim($line))[1];
    return $submodule;
}, array_filter(explode(PHP_EOL, shell_exec('git submodule status')))));


foreach ($submodules as $submodule) {
    chdir(__DIR__ . '/../' . $submodule);

    $output = shell_exec('git st');
    if (strpos($output, 'Changes') || strpos($output, 'diverged') || strpos($output, 'publish your local commits')) {
        echo str_repeat('-', 20) . PHP_EOL;
        echo '   ' . $submodule . PHP_EOL;
        echo str_repeat('-', 20) . PHP_EOL;
        echo $output . PHP_EOL;
    }
}

