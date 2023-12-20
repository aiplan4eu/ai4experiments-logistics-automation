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
            "initialize_robot__state": "idle",
            "execute_offline_tasks__state": "idle",
            "execute_imu_calibration__state": "idle",
        },
        "steps": [
            {
                "description": "The robot is arrived at the charger station (battery_charging = charging) because its battery was low (battery_level = low). "\
                                "It is ready to start some initialization procedures.",
                "state_change": {}
            },
            {
                "description": "The initialization procedure has been started.",
                "state_change": {
                    "initialize_robot__state": "running"
                }
            },
        ]
    }
}

