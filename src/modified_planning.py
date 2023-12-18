import networkx as nx
import logging
from typing import Tuple
from up_graphene_engine.engine import  GrapheneEngine
from gui import Gui

from experiment_definitions import experiments

from unified_planning.shortcuts import *
import unified_planning as up
import unified_planning.engines
import unified_planning.model
import unified_planning.model.metrics

get_environment().credits_stream = None



def planning(engine: GrapheneEngine, gui: Gui, reload_page):
    logging.info("Generating planning problem...")

    environment = up.environment.get_environment()

    action_state = UserType("action_state")
    battery_charging_type = UserType("battery_charging_type")
    battery_level_type = UserType("battery_level_type")
    capabilities_available_type = UserType("capabilities_available_type")
    have_error_report_type = UserType("have_error_report_type")
    hw_self_test_required_type = UserType("hw_self_test_required_type")
    job_available_type = UserType("job_available_type")
    param_hw_self_test_enabled_type = UserType("param_hw_self_test_enabled_type")
    param_recharging_enabled_type = UserType("param_recharging_enabled_type")
    power_saving_state_type = UserType("power_saving_state_type")
    have_recharging_job_type = UserType("have_recharging_job_type")
    robot_needs_execute_offline_tasks_type = UserType("robot_needs_execute_offline_tasks_type")
    robot_needs_initialization_type = UserType("robot_needs_initialization_type")
    tower_busy_type = UserType("tower_busy_type")

    battery_charging = Fluent("battery_charging", battery_charging_type) # NOTE starts as discharging and there are no actions that sets it in a different way (but some require it to be in another way)
    battery_level = Fluent("battery_level", battery_level_type) # NOTE never used
    capabilities_available = Fluent("capabilities_available", capabilities_available_type) # NOTE only red in execute__acknowledge_error_report and never changed
    have_error_report = Fluent("have_error_report", have_error_report_type)
    hw_self_test_required = Fluent("hw_self_test_required", hw_self_test_required_type) # NOTE Set to false and never written (required both to be F and T by some actions)
    job_available = Fluent("job_available", job_available_type) # NOTE never used (neither write or read)
    param_hw_self_test_enabled = Fluent("param_hw_self_test_enabled", param_hw_self_test_enabled_type) # NOTE starts as T, required to be F in 2 actions, but no action can set it to F
    param_recharging_enabled = Fluent("param_recharging_enabled", param_recharging_enabled_type) # NOTE never used
    power_saving_state = Fluent("power_saving_state", power_saving_state_type)
    have_recharging_job = Fluent("have_recharging_job", have_recharging_job_type) # NOTE never used

    robot_needs_execute_offline_tasks = Fluent("robot_needs_execute_offline_tasks", robot_needs_execute_offline_tasks_type)
    robot_needs_initialization = Fluent("robot_needs_initialization", robot_needs_initialization_type)
    tower_busy = Fluent("tower_busy", tower_busy_type)
    acknowledge_error_report__state = Fluent("acknowledge_error_report__state", action_state)
    execute_hw_self_test__state = Fluent("execute_hw_self_test__state", action_state)
    execute_imu_calibration__state = Fluent("execute_imu_calibration__state", action_state)
    execute_offline_tasks__state = Fluent("execute_offline_tasks__state", action_state)
    initialize_robot__state = Fluent("initialize_robot__state", action_state)
    power_saving_action__state = Fluent("power_saving_action__state", action_state)

    idle = Object("idle", action_state)
    running = Object("running", action_state)
    aborting = Object("aborting", action_state)
    executed = Object("executed", action_state)

    battery_charging_charging = Object("battery_charging_charging", battery_charging_type)
    battery_charging_discharging = Object("battery_charging_discharging", battery_charging_type)
    battery_charging_not_charging = Object("battery_charging_not_charging", battery_charging_type)
    battery_charging_unk = Object("battery_charging_unk", battery_charging_type) # Never used

    battery_level_critical = Object("battery_level_critical", battery_level_type)
    battery_level_low = Object("battery_level_low", battery_level_type)
    battery_level_average = Object("battery_level_average", battery_level_type)
    battery_level_full = Object("battery_level_full", battery_level_type)
    battery_level_unk = Object("battery_level_unk", battery_level_type) # never used

    capabilities_available_true = Object("capabilities_available_true", capabilities_available_type)
    capabilities_available_false = Object("capabilities_available_false", capabilities_available_type)
    capabilities_available_unk = Object("capabilities_available_unk", capabilities_available_type) #never used

    have_error_report_false = Object("have_error_report_false", have_error_report_type)
    have_error_report_true_acknowledgeable = Object("have_error_report_true_acknowledgeable", have_error_report_type)
    have_error_report_true_not_acknowledgeable = Object("have_error_report_true_not_acknowledgeable", have_error_report_type)
    have_error_report_unk = Object("have_error_report_unk", have_error_report_type) # never used

    hw_self_test_required_true = Object("hw_self_test_required_true", hw_self_test_required_type)
    hw_self_test_required_false = Object("hw_self_test_required_false", hw_self_test_required_type)
    hw_self_test_required_unk = Object("hw_self_test_required_unk", hw_self_test_required_type) # never used

    job_available_true = Object("job_available_true", job_available_type)
    job_available_false = Object("job_available_false", job_available_type)
    job_available_unk = Object("job_available_unk", job_available_type) # never used

    param_hw_self_test_enabled_true = Object("param_hw_self_test_enabled_true", param_hw_self_test_enabled_type)
    param_hw_self_test_enabled_false = Object("param_hw_self_test_enabled_false", param_hw_self_test_enabled_type)
    param_hw_self_test_enabled_unk = Object("param_hw_self_test_enabled_unk", param_hw_self_test_enabled_type)  # never used

    param_recharging_enabled_true = Object("param_recharging_enabled_true", param_recharging_enabled_type)
    param_recharging_enabled_false = Object("param_recharging_enabled_false", param_recharging_enabled_type)
    param_recharging_enabled_unk = Object("param_recharging_enabled_unk", param_recharging_enabled_type)  # never used

    power_saving_state_activating = Object("power_saving_state_activating", power_saving_state_type)
    power_saving_state_activated = Object("power_saving_state_activated", power_saving_state_type)
    power_saving_state_deactivating = Object("power_saving_state_deactivating", power_saving_state_type)
    power_saving_state_deactivated = Object("power_saving_state_deactivated", power_saving_state_type)
    power_saving_state_unknown = Object("power_saving_state_unknown", power_saving_state_type)
    power_saving_state_unk = Object("power_saving_state_unk", power_saving_state_type)  # never used

    have_recharging_job_UNK = Object("have_recharging_job_UNK", have_recharging_job_type) # never used
    have_recharging_job_true = Object("have_recharging_job_true", have_recharging_job_type)
    have_recharging_job_false = Object("have_recharging_job_false", have_recharging_job_type)

    robot_needs_execute_offline_tasks_UNK = Object("robot_needs_execute_offline_tasks_UNK", robot_needs_execute_offline_tasks_type)  # never used
    robot_needs_execute_offline_tasks_true = Object("robot_needs_execute_offline_tasks_true", robot_needs_execute_offline_tasks_type)
    robot_needs_execute_offline_tasks_false = Object("robot_needs_execute_offline_tasks_false", robot_needs_execute_offline_tasks_type)

    robot_needs_initialization_UNK = Object("robot_needs_initialization_UNK", robot_needs_initialization_type) # never used
    robot_needs_initialization_true = Object("robot_needs_initialization_true", robot_needs_initialization_type)
    robot_needs_initialization_false = Object("robot_needs_initialization_false", robot_needs_initialization_type)

    tower_busy_UNK = Object("tower_busy_UNK", tower_busy_type)  # never used
    tower_busy_true = Object("tower_busy_true", tower_busy_type)
    tower_busy_false = Object("tower_busy_false", tower_busy_type)

    problem_initial_defaults = {}

    problem = Problem("yaddl_problem", environment, initial_defaults=problem_initial_defaults)
    problem.add_object(idle)
    problem.add_object(running)
    problem.add_object(aborting)
    problem.add_object(executed)
    problem.add_object(battery_charging_charging)
    problem.add_object(battery_charging_discharging)
    problem.add_object(battery_charging_not_charging)
    problem.add_object(battery_charging_unk)
    problem.add_object(battery_level_critical)
    problem.add_object(battery_level_low)
    problem.add_object(battery_level_average)
    problem.add_object(battery_level_full)
    problem.add_object(battery_level_unk)
    problem.add_object(capabilities_available_true)
    problem.add_object(capabilities_available_false)
    problem.add_object(capabilities_available_unk)
    problem.add_object(have_error_report_false)
    problem.add_object(have_error_report_true_acknowledgeable)
    problem.add_object(have_error_report_true_not_acknowledgeable)
    problem.add_object(have_error_report_unk)
    problem.add_object(hw_self_test_required_true)
    problem.add_object(hw_self_test_required_false)
    problem.add_object(hw_self_test_required_unk)
    problem.add_object(job_available_true)
    problem.add_object(job_available_false)
    problem.add_object(job_available_unk)
    problem.add_object(param_hw_self_test_enabled_true)
    problem.add_object(param_hw_self_test_enabled_false)
    problem.add_object(param_hw_self_test_enabled_unk)
    problem.add_object(param_recharging_enabled_true)
    problem.add_object(param_recharging_enabled_false)
    problem.add_object(param_recharging_enabled_unk)
    problem.add_object(power_saving_state_activating)
    problem.add_object(power_saving_state_activated)
    problem.add_object(power_saving_state_deactivating)
    problem.add_object(power_saving_state_deactivated)
    problem.add_object(power_saving_state_unknown)
    problem.add_object(power_saving_state_unk)
    problem.add_object(have_recharging_job_UNK)
    problem.add_object(have_recharging_job_true)
    problem.add_object(have_recharging_job_false)
    problem.add_object(robot_needs_execute_offline_tasks_UNK)
    problem.add_object(robot_needs_execute_offline_tasks_true)
    problem.add_object(robot_needs_execute_offline_tasks_false)
    problem.add_object(robot_needs_initialization_UNK)
    problem.add_object(robot_needs_initialization_true)
    problem.add_object(robot_needs_initialization_false)
    problem.add_object(tower_busy_UNK)
    problem.add_object(tower_busy_true)
    problem.add_object(tower_busy_false)

    problem.add_fluent(battery_charging, default_initial_value=ObjectExp(battery_charging_discharging))
    problem.add_fluent(battery_level, default_initial_value=ObjectExp(battery_level_average))
    problem.add_fluent(capabilities_available, default_initial_value=ObjectExp(capabilities_available_true))
    problem.add_fluent(have_error_report, default_initial_value=ObjectExp(have_error_report_false))
    problem.add_fluent(hw_self_test_required, default_initial_value=ObjectExp(hw_self_test_required_false))
    problem.add_fluent(job_available, default_initial_value=ObjectExp(job_available_false))
    problem.add_fluent(param_hw_self_test_enabled, default_initial_value=ObjectExp(param_hw_self_test_enabled_true))
    problem.add_fluent(param_recharging_enabled, default_initial_value=ObjectExp(param_recharging_enabled_true))
    problem.add_fluent(power_saving_state, default_initial_value=ObjectExp(power_saving_state_deactivated))
    problem.add_fluent(have_recharging_job, default_initial_value=ObjectExp(have_recharging_job_false))
    problem.add_fluent(robot_needs_execute_offline_tasks, default_initial_value=ObjectExp(robot_needs_execute_offline_tasks_true))
    problem.add_fluent(robot_needs_initialization, default_initial_value=ObjectExp(robot_needs_initialization_true))
    problem.add_fluent(tower_busy, default_initial_value=ObjectExp(tower_busy_false))
    problem.add_fluent(acknowledge_error_report__state, default_initial_value=ObjectExp(idle))
    problem.add_fluent(execute_hw_self_test__state, default_initial_value=ObjectExp(idle))
    problem.add_fluent(execute_imu_calibration__state, default_initial_value=ObjectExp(idle))
    problem.add_fluent(execute_offline_tasks__state, default_initial_value=ObjectExp(idle))
    problem.add_fluent(initialize_robot__state, default_initial_value=ObjectExp(idle))
    problem.add_fluent(power_saving_action__state, default_initial_value=ObjectExp(idle))

    cur_experiment = "parallel_actions"
    cur_step = 0

    for key, val in experiments[cur_experiment]["initial_state"].items():
        problem.set_initial_value(problem.fluent(key), problem.object(key + "_" + val))

    for c in range(0, cur_step):
        for key, val in experiments[cur_experiment]["steps"][cur_step]["state_change"].items():
            problem.set_initial_value(problem.fluent(key), problem.object(key + "_" + val))

    act_abort__execute_hw_self_test = InstantaneousAction("abort__execute_hw_self_test")
    act_abort__execute_hw_self_test.add_precondition(Equals(execute_hw_self_test__state, running))
    act_abort__execute_hw_self_test.add_effect(execute_hw_self_test__state, aborting)
    problem.add_action(act_abort__execute_hw_self_test)

    act_abort__execute_imu_calibration = InstantaneousAction("abort__execute_imu_calibration")
    act_abort__execute_imu_calibration.add_precondition(Equals(execute_imu_calibration__state, running))
    act_abort__execute_imu_calibration.add_effect(execute_imu_calibration__state, aborting)
    problem.add_action(act_abort__execute_imu_calibration)

    act_abort__execute_offline_tasks = InstantaneousAction("abort__execute_offline_tasks")
    act_abort__execute_offline_tasks.add_precondition(Equals(execute_offline_tasks__state, running))
    act_abort__execute_offline_tasks.add_effect(execute_offline_tasks__state, aborting)
    problem.add_action(act_abort__execute_offline_tasks)

    act_abort__initialize_robot = InstantaneousAction("abort__initialize_robot")
    act_abort__initialize_robot.add_precondition(Equals(initialize_robot__state, running))
    act_abort__initialize_robot.add_effect(initialize_robot__state, aborting)
    problem.add_action(act_abort__initialize_robot)

    act_abort__power_saving_action = InstantaneousAction("abort__power_saving_action")
    act_abort__power_saving_action.add_precondition(Equals((power_saving_action__state), (running)))
    act_abort__power_saving_action.add_effect((power_saving_action__state), (aborting))
    problem.add_action(act_abort__power_saving_action)

    act_execute__acknowledge_error_report = InstantaneousAction("execute__acknowledge_error_report")
    act_execute__acknowledge_error_report.add_precondition(And(And(Equals((have_error_report), (have_error_report_true_not_acknowledgeable)), Equals((capabilities_available), (capabilities_available_true))), Equals((acknowledge_error_report__state), (idle))))
    act_execute__acknowledge_error_report.add_effect((acknowledge_error_report__state), (executed))
    problem.add_action(act_execute__acknowledge_error_report)

    act_on_aborted__execute_hw_self_test = InstantaneousAction("on_aborted__execute_hw_self_test")
    act_on_aborted__execute_hw_self_test.add_precondition(Equals((execute_hw_self_test__state), (aborting)))
    act_on_aborted__execute_hw_self_test.add_effect((execute_hw_self_test__state), (idle))
    act_on_aborted__execute_hw_self_test.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    act_on_aborted__execute_hw_self_test.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_aborted__execute_hw_self_test)

    act_on_aborted__execute_imu_calibration = InstantaneousAction("on_aborted__execute_imu_calibration")
    act_on_aborted__execute_imu_calibration.add_precondition(Equals((execute_imu_calibration__state), (aborting)))
    act_on_aborted__execute_imu_calibration.add_effect((execute_imu_calibration__state), (idle))
    problem.add_action(act_on_aborted__execute_imu_calibration)

    act_on_aborted__execute_offline_tasks = InstantaneousAction("on_aborted__execute_offline_tasks")
    act_on_aborted__execute_offline_tasks.add_precondition(Equals((execute_offline_tasks__state), (aborting)))
    act_on_aborted__execute_offline_tasks.add_effect((execute_offline_tasks__state), (idle))
    problem.add_action(act_on_aborted__execute_offline_tasks)

    act_on_aborted__initialize_robot = InstantaneousAction("on_aborted__initialize_robot")
    act_on_aborted__initialize_robot.add_precondition(Equals((initialize_robot__state), (aborting)))
    act_on_aborted__initialize_robot.add_effect((initialize_robot__state), (idle))
    act_on_aborted__initialize_robot.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_aborted__initialize_robot)

    act_on_aborted__power_saving_action = InstantaneousAction("on_aborted__power_saving_action")
    act_on_aborted__power_saving_action.add_precondition(Equals((power_saving_action__state), (aborting)))
    act_on_aborted__power_saving_action.add_effect((power_saving_action__state), (idle))
    act_on_aborted__power_saving_action.add_effect((power_saving_state), (power_saving_state_deactivated))
    act_on_aborted__power_saving_action.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    problem.add_action(act_on_aborted__power_saving_action)

    act_on_failure__acknowledge_error_report = InstantaneousAction("on_failure__acknowledge_error_report")
    act_on_failure__acknowledge_error_report.add_precondition(Equals((acknowledge_error_report__state), (executed)))
    act_on_failure__acknowledge_error_report.add_effect((acknowledge_error_report__state), (idle))
    problem.add_action(act_on_failure__acknowledge_error_report)

    act_on_failure__execute_hw_self_test = InstantaneousAction("on_failure__execute_hw_self_test")
    act_on_failure__execute_hw_self_test.add_precondition(Equals((execute_hw_self_test__state), (running)))
    act_on_failure__execute_hw_self_test.add_effect((execute_hw_self_test__state), (idle))
    act_on_failure__execute_hw_self_test.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    act_on_failure__execute_hw_self_test.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_failure__execute_hw_self_test)

    act_on_failure__execute_imu_calibration = InstantaneousAction("on_failure__execute_imu_calibration")
    act_on_failure__execute_imu_calibration.add_precondition(Equals((execute_imu_calibration__state), (running)))
    act_on_failure__execute_imu_calibration.add_effect((execute_imu_calibration__state), (idle))
    problem.add_action(act_on_failure__execute_imu_calibration)

    act_on_failure__execute_offline_tasks = InstantaneousAction("on_failure__execute_offline_tasks")
    act_on_failure__execute_offline_tasks.add_precondition(Equals((execute_offline_tasks__state), (running)))
    act_on_failure__execute_offline_tasks.add_effect((execute_offline_tasks__state), (idle))
    problem.add_action(act_on_failure__execute_offline_tasks)

    act_on_failure__initialize_robot = InstantaneousAction("on_failure__initialize_robot")
    act_on_failure__initialize_robot.add_precondition(Equals((initialize_robot__state), (running)))
    act_on_failure__initialize_robot.add_effect((initialize_robot__state), (idle))
    act_on_failure__initialize_robot.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_failure__initialize_robot)

    act_on_failure__power_saving_action = InstantaneousAction("on_failure__power_saving_action")
    act_on_failure__power_saving_action.add_precondition(Equals((power_saving_action__state), (running)))
    act_on_failure__power_saving_action.add_effect((power_saving_action__state), (idle))
    act_on_failure__power_saving_action.add_effect((power_saving_state), (power_saving_state_deactivated))
    act_on_failure__power_saving_action.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    problem.add_action(act_on_failure__power_saving_action)

    act_on_success__acknowledge_error_report = InstantaneousAction("on_success__acknowledge_error_report")
    act_on_success__acknowledge_error_report.add_precondition(Equals((acknowledge_error_report__state), (executed)))
    act_on_success__acknowledge_error_report.add_effect((acknowledge_error_report__state), (idle))
    act_on_success__acknowledge_error_report.add_effect((have_error_report), (have_error_report_false))
    problem.add_action(act_on_success__acknowledge_error_report)

    act_on_success__execute_hw_self_test = InstantaneousAction("on_success__execute_hw_self_test")
    act_on_success__execute_hw_self_test.add_precondition(Equals((execute_hw_self_test__state), (running)))
    act_on_success__execute_hw_self_test.add_effect((execute_hw_self_test__state), (idle))
    act_on_success__execute_hw_self_test.add_effect((hw_self_test_required), (hw_self_test_required_false))
    act_on_success__execute_hw_self_test.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    act_on_success__execute_hw_self_test.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_success__execute_hw_self_test)

    act_on_success__execute_imu_calibration = InstantaneousAction("on_success__execute_imu_calibration")
    act_on_success__execute_imu_calibration.add_precondition(Equals((execute_imu_calibration__state), (running)))
    act_on_success__execute_imu_calibration.add_effect((execute_imu_calibration__state), (idle))
    problem.add_action(act_on_success__execute_imu_calibration)

    act_on_success__execute_offline_tasks = InstantaneousAction("on_success__execute_offline_tasks")
    act_on_success__execute_offline_tasks.add_precondition(Equals((execute_offline_tasks__state), (running)))
    act_on_success__execute_offline_tasks.add_effect((execute_offline_tasks__state), (idle))
    act_on_success__execute_offline_tasks.add_effect((robot_needs_execute_offline_tasks), (robot_needs_execute_offline_tasks_false))
    problem.add_action(act_on_success__execute_offline_tasks)

    act_on_success__initialize_robot = InstantaneousAction("on_success__initialize_robot")
    act_on_success__initialize_robot.add_precondition(Equals((initialize_robot__state), (running)))
    act_on_success__initialize_robot.add_effect((initialize_robot__state), (idle))
    act_on_success__initialize_robot.add_effect((robot_needs_initialization), (robot_needs_initialization_false))
    act_on_success__initialize_robot.add_effect((tower_busy), (tower_busy_false))
    problem.add_action(act_on_success__initialize_robot)

    act_on_success__power_saving_action = InstantaneousAction("on_success__power_saving_action")
    act_on_success__power_saving_action.add_precondition(Equals((power_saving_action__state), (running)))
    act_on_success__power_saving_action.add_effect((power_saving_action__state), (idle))
    act_on_success__power_saving_action.add_effect((power_saving_state), (power_saving_state_deactivated))
    act_on_success__power_saving_action.add_effect((robot_needs_initialization), (robot_needs_initialization_true))
    problem.add_action(act_on_success__power_saving_action)

    act_start__execute_hw_self_test = InstantaneousAction("start__execute_hw_self_test")
    act_start__execute_hw_self_test.add_precondition(And(And(Equals((hw_self_test_required), (hw_self_test_required_true)), Equals((battery_charging), (battery_charging_charging)), Equals((robot_needs_initialization), (robot_needs_initialization_false)), Not(Equals((tower_busy), (tower_busy_true))), Or(Equals((power_saving_state), (power_saving_state_deactivated)), Equals((power_saving_state), (power_saving_state_unknown)))), Equals((execute_hw_self_test__state), (idle))))
    act_start__execute_hw_self_test.add_effect((execute_hw_self_test__state), (running))
    act_start__execute_hw_self_test.add_effect((tower_busy), (tower_busy_true))
    problem.add_action(act_start__execute_hw_self_test)

    act_start__execute_imu_calibration = InstantaneousAction("start__execute_imu_calibration")
    act_start__execute_imu_calibration.add_precondition(And(And(Equals((robot_needs_initialization), (robot_needs_initialization_false)), Equals((execute_hw_self_test__state), (idle)), Or(Equals((hw_self_test_required), (hw_self_test_required_false)), Equals((param_hw_self_test_enabled), (param_hw_self_test_enabled_false)), Not(Equals((battery_charging), (battery_charging_charging))))), Equals((execute_imu_calibration__state), (idle))))
    act_start__execute_imu_calibration.add_effect((execute_imu_calibration__state), (running))
    problem.add_action(act_start__execute_imu_calibration)

    act_start__execute_offline_tasks = InstantaneousAction("start__execute_offline_tasks")
    act_start__execute_offline_tasks.add_precondition(And(And(Equals((robot_needs_execute_offline_tasks), (robot_needs_execute_offline_tasks_true)), Equals((robot_needs_initialization), (robot_needs_initialization_false)), Equals((execute_hw_self_test__state), (idle)), Or(Not(Equals((battery_charging), (battery_charging_charging))), Equals((hw_self_test_required), (hw_self_test_required_false)), Equals((param_hw_self_test_enabled), (param_hw_self_test_enabled_false)))), Equals((execute_offline_tasks__state), (idle))))
    act_start__execute_offline_tasks.add_effect((execute_offline_tasks__state), (running))
    problem.add_action(act_start__execute_offline_tasks)

    act_start__initialize_robot = InstantaneousAction("start__initialize_robot")
    act_start__initialize_robot.add_precondition(And(And(Equals((robot_needs_initialization), (robot_needs_initialization_true)), Equals((tower_busy), (tower_busy_false))), Equals((initialize_robot__state), (idle))))
    act_start__initialize_robot.add_effect((initialize_robot__state), (running))
    act_start__initialize_robot.add_effect((tower_busy), (tower_busy_true))
    problem.add_action(act_start__initialize_robot)

    act_start__power_saving_action = InstantaneousAction("start__power_saving_action")
    act_start__power_saving_action.add_precondition(And(And(Equals((power_saving_state), (power_saving_state_deactivated)), Equals((execute_hw_self_test__state), (idle))), Equals((power_saving_action__state), (idle))))
    act_start__power_saving_action.add_effect((power_saving_action__state), (running))
    act_start__power_saving_action.add_effect((power_saving_state), (power_saving_state_activated))
    problem.add_action(act_start__power_saving_action)

    # problem.add_goal(goal=And(Or(Equals((have_error_report), (have_error_report_false)), Equals((have_error_report), (have_error_report_true_acknowledgeable))), Equals((robot_needs_initialization), (robot_needs_initialization_false)), Equals((tower_busy), (tower_busy_false)), Equals((robot_needs_execute_offline_tasks), (robot_needs_execute_offline_tasks_false)), Equals((execute_imu_calibration__state), (running))))

    problem.add_goal(Or(Equals(have_error_report, have_error_report_false), Equals(have_error_report, have_error_report_true_acknowledgeable)))
    problem.add_goal(Equals(robot_needs_initialization, robot_needs_initialization_false))
    problem.add_goal(Equals(tower_busy, tower_busy_false))
    problem.add_goal(Equals(robot_needs_execute_offline_tasks, robot_needs_execute_offline_tasks_false))
    problem.add_goal(Equals(execute_imu_calibration__state, running))

    costs = {}
    costs[act_abort__execute_hw_self_test] = 1
    costs[act_abort__execute_imu_calibration] = 1
    costs[act_abort__execute_offline_tasks] = 1
    costs[act_abort__initialize_robot] = 1
    costs[act_abort__power_saving_action] = 1

    costs[act_execute__acknowledge_error_report] = 1

    costs[act_on_aborted__execute_hw_self_test] = 1
    costs[act_on_aborted__execute_imu_calibration] = 1
    costs[act_on_aborted__execute_offline_tasks] = 1
    costs[act_on_aborted__initialize_robot] = 1
    costs[act_on_aborted__power_saving_action] = 1

    costs[act_on_failure__acknowledge_error_report] = 1
    costs[act_on_failure__execute_hw_self_test] = 100
    costs[act_on_failure__execute_imu_calibration] = 10
    costs[act_on_failure__execute_offline_tasks] = 10
    costs[act_on_failure__initialize_robot] = 10
    costs[act_on_failure__power_saving_action] = 10

    costs[act_on_success__acknowledge_error_report] = 1
    costs[act_on_success__execute_hw_self_test] = 100
    costs[act_on_success__execute_imu_calibration] = 10
    costs[act_on_success__execute_offline_tasks] = 10
    costs[act_on_success__initialize_robot] = 10
    costs[act_on_success__power_saving_action] = 10

    costs[act_start__execute_hw_self_test] = 1
    costs[act_start__execute_imu_calibration] = 1
    costs[act_start__execute_offline_tasks] = 1
    costs[act_start__initialize_robot] = 1
    costs[act_start__power_saving_action] = 1

    problem.add_quality_metric(MinimizeActionCosts(costs, None))


    comp_kinds = [CompilationKind.USERTYPE_FLUENTS_REMOVING, CompilationKind.DISJUNCTIVE_CONDITIONS_REMOVING]
    with Compiler(problem_kind=problem.kind, compilation_kind=CompilationKind.USERTYPE_FLUENTS_REMOVING) as compiler:

        comp_res = compiler.compile(problem)

        with Compiler(problem_kind=comp_res.problem.kind, compilation_kind=CompilationKind.DISJUNCTIVE_CONDITIONS_REMOVING) as compiler_2:

            comp_res_2 = compiler_2.compile(comp_res.problem)

    logging.info("Planning...")

    res = engine.solve(comp_res_2.problem)
    plan = None if res.plan is None else res.plan.replace_action_instances(comp_res_2.map_back_action_instance).replace_action_instances(comp_res.map_back_action_instance)

    return plan
