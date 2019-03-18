<?php

namespace PHPSTORM_META {

    override(
        \Manager_Container::getManager(0),
        type(0)
    );
    override(
        \EntityManager_Interface::find(0, 1),
        type(1)
    );
    override(
        \EntityManager_Interface::selectOne(0, 1),
        type(1)
    );
    override(
        \EntityManager_Interface::select(0, 1),
        (array) type(1) // todo make it work !!! https://youtrack.jetbrains.com/issue/WI-27832
    );
    override(
        \Location_Manager_Location::getLocationType(0, 1),
        type(1)
    );
}
