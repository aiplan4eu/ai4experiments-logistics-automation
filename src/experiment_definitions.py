experiments = {
    "parallel_actions": {
        "initial_state": {
            "capabilities_available": "true",
            "job_available": "false",
            "battery_charging": "charging",
            "battery_level": "low",
            "have_error_report": "false",
            "hw_self_test_required": "false",
            "power_saving_state": "deactivated",
            "robot_needs_initialization": "true",
            "initialize_robot__state": "idle",
            "execute_offline_tasks__state": "idle",
            "execute_imu_calibration__state": "idle",
            "execute_hw_self_test__state": "idle",
        },
        "steps": [
            {
                "description": "The robot is arrived at the charger station (battery_charging = charging) because its battery was low (battery_level = low). "
                                "It is ready to start some initialization procedures. Click on the SOLVE button to see the result of the planner in this situation.",
                "state_change": {}
            },
            {
                "description": "The initialization procedure has been started. Click on the SOLVE button to see the plan advancing a step. "
                        "Now the executor will wait for the initialization to (successfully) finish (the first action in the plan is an on_*). ",
                "state_change": {
                    "initialize_robot__state": "running"
                }
            },
            {
                "description": "The initialization procedure has been successfully executed. Its state is back to 'idle', but the robot does not need to be initialized anymore "\
                        "(robot_needs_initialization = false).",
                "state_change": {
                    "initialize_robot__state": "idle",
                    "robot_needs_initialization": "false",
                }
            },
            {
                "description": "The robot now started the set of offline activities. If you click on SOLVE, you will see that another, parallel, activity can be performed: "\
                        "the IMU calibration. The two actions are not mutually exclusive and the planner optimally chooses to run both in parallel",
                "state_change": {
                    "initialize_robot__state": "idle",
                    "robot_needs_initialization": "false",
                    "execute_offline_tasks__state": "running",
                }
            },
            {
                "description": "The robot is now executing both the offline activities and the IMU calibration (both the __state variables are running). "\
                        "Clicking on SOLVE now will show an empty plan, since the goal has been already reached.",
                "state_change": {
                    "initialize_robot__state": "idle",
                    "robot_needs_initialization": "false",
                    "execute_offline_tasks__state": "running",
                    "execute_imu_calibration__state": "running",
                }
            },
        ]
    },
    "lost_capabilities": {
        "initial_state": {
            "capabilities_available": "true",
            "job_available": "false",
            "battery_charging": "charging",
            "battery_level": "average",
            "have_error_report": "false",
            "hw_self_test_required": "false",
            "power_saving_state": "deactivated",
            "robot_needs_initialization": "false",
            "initialize_robot__state": "idle",
            "execute_offline_tasks__state": "idle",
            "execute_imu_calibration__state": "idle",
            "execute_hw_self_test__state": "idle",
        },
        "steps": [
            {
                "description": "The system is ready to start its activities, because it is on the charger, no job has been sent and, in this case, "\
                        "it already performed the initialization procedure (robot_needs_initialization is now false).",
                "state_change": {}
            },
            {
                "description": "The robot started one of the two activities (execute_offline_tasks) that are to be considered after the initialization.",
                "state_change": {
                    "execute_offline_tasks__state": "running",
                }
            },
            {
                "description": "While the robot is performing its offline tasks, something started to malfunction and the robot loses some of its capabilities "\
                        "(capabilities_available = false). "\
                        "The planner in this state changes the goal and tries to have all activities in an 'idle' state, in order to cleanly enter the (external) "\
                        "recovery procedure. If you click on SOLVE, you will see that the optimal choice in this case is to abort the offline tasks and wait "\
                        "for its abortion, instead of waiting for it to finish.",
                "state_change": {
                    "capabilities_available": "false",
                },
                "goal": "goal1"
            },
        ],
    },
    "run_until_job": {
        "initial_state": {
            "capabilities_available": "true",
            "job_available": "false",
            "battery_charging": "charging",
            "battery_level": "average",
            "have_error_report": "false",
            "hw_self_test_required": "true",
            "power_saving_state": "deactivated",
            "robot_needs_initialization": "true",
            "initialize_robot__state": "idle",
            "execute_offline_tasks__state": "idle",
            "execute_imu_calibration__state": "idle",
            "execute_hw_self_test__state": "idle",
        },
        "steps": [
            {
                "description": "In this experiment, the planner will guide the robot to start the usual initialization procedure and afterwards the other activities. "\
                        "In this case, the robot also needs to perform the hardware self test (hw_self_test_required = true). "\
                        "When you run the planner with SOLVE, you can see that the planner takes care both to have an initialized robot as a precondition for "\
                        "starting the hardware self test, as well as considering that the hardware self test leaves the robot in an uninitialized state, so it needs "\
                        "to be initialized again. "\
                        "At some point (Step 4), a new job arrives (job_available becomes true) this leads to changing the goal, aborting all activities and lead the robot "\
                        "to a clean state (initializing again, because the hardware self test leaves it in an uninitialized state) before going to execute the job.",
                "state_change": {}
            },
            {
                "description": "The initialization procedure has been started, if you click on SOLVE, you will see that the current plan is to wait for this procedure to "
                        "finish, then perform a required hardware self test and then perform other activities.",
                "state_change": {
                    "initialize_robot__state": "running"
                }
            },
            {
                "description": "The initialization procedure has been completed, now the plan guides the robot to perform a hardware self test, because the current "
                        "state variable hardware_self_test_required is true.",
                "state_change": {
                    "initialize_robot__state": "idle",
                    "robot_needs_initialization": "false",
                }
            },
            {
                "description": "Now the robot is performing a hardware self test (execute_hw_self_test__state is true), clicking on SOLVE will show that the plan is "
                        "to wait for this test to finish, then re-initialize the robot (because the hardware self test leaves the robot in a 'dirty' state) and then "
                        "start the usual offline activities.",
                "state_change": {
                    "execute_hw_self_test__state": "running"
                }
            },
            {
                "description": "A job is now available, while the robot was performing the hardware self test. The robot needs a clean exit from its offline activities. "
                        "for this reason, the planner guides the robot to abort the currently hardware self test and then to re-initialize the robot, as the hardware self test "
                        "leaves the robot in an un-initialized state, so the robot needs to be re-initialized in order to start executing the job.",
                "state_change": {
                    "job_available": "true",
                    "execute_hw_self_test__state": "running"
                },
                "goal": "goal1"
            }
        ]
    }
}

