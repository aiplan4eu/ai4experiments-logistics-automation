import justpy as jp

from gui import Gui, Mode

LEFT_MARGIN, RIGHT_MARGIN = " margin-left: 10px; ", " margin-right: 20px; "

TITLE_DIV_CLASS = "grid justify-between gap-2 grid-cols-3"
TITLE_DIV_STYLE = "grid-template-columns: auto auto auto; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

TITLE_TEXT_DIV_STYLE = "font-size: 80px; text-align: center; text-weight: bold;"

DESCRIPTION_STYLE = "margin-top: 15px; font-size: 16px;" + LEFT_MARGIN + RIGHT_MARGIN
DESCRIPTION_TEXT = """
In this case, the planner is deployed on a robot running in a logistics automation environment.
The specific situation, in this case, is related to the operations that the robot has to perform
when it is not performing a job, e.g., (re-)initializing its motors, perform some hardware self-test procedures,
calibrate the IMU, etc.
Choose the initial situation and press SOLVE for the initial plan. In this use-case, the durative actions
are split into multiple instantaneous actions, that represent their start, abortion and final success, abortion or failure.
Afterwards, by advancing the STEP field and pressing SOLVE again, the system simulate the advancement of the state of the
durative actions and/or some possible unexpected change in the state, that require a complete replanning.
"""
SINGLE_DESCRIPTION_STYLE = LEFT_MARGIN + RIGHT_MARGIN


MAIN_BODY_DIV_CLASS = "grid justify-between grid-cols-3 gap-7"
MAIN_BODY_DIV_STYLE = "grid-template-columns: max-content 45% 0.9fr; column-gap: 15px; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN
# MAIN_BODY_DIV_STYLE = "grid-template-columns: minmax(max-content, 25%) minmax(max-content, 25%) 10px minmax(max-content, 33%); width: 100vw; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

ACTIONS_DIV_CLASS = "grid"
# Setting height to 0 it'sa trick to solve the problem of the goal div changing size
ACTIONS_DIV_STYLE = f"grid-template-columns: auto auto; font-size: 30px; font-weight: semibold; height: 0px;"

INPUT_DESCRIPTION_P_CLASS = ""
INPUT_DESCRIPTION_P_STYLE = "font-size: 16px; font-weight: normal; margin-top: 10px;"

TEXT_WIDTH = 100 # px
COL_GAP = 4 # px
TEXT_INPUT_P_CLASS = ""
TEXT_INPUT_P_STYLE = f"font-weight: normal; font-size: 16px; border: 0.9px solid #000; background-color: #e1eff7; padding: 5px; width: {TEXT_WIDTH}px; margin-top: 5px; margin-left: 5px;"

ADD_BUTTON_CLASS = "bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2"
ADD_BUTTON_STYLE = f"font-weight: semibold; font-size: 20px; width: {TEXT_WIDTH}px; margin-top: 5px;"

GOALS_DIV_CLASS = ""
GOALS_DIV_STYLE = "font-size: 30px; font-weight: semibold; height: 0px;"

CLEAR_SOLVE_BUTTONS_DIV_CLASS = "flex grid-cols-2"
CLEAR_SOLVE_BUTTONS_DIV_STYLE = f"column-gap: {COL_GAP}px;"

CLEAR_SOLVE_BUTTONS_CLASS = ADD_BUTTON_CLASS
CLEAR_SOLVE_BUTTONS_STYLE = "font-weight: semibold; font-size: 20px;"

PLAN_DIV_CLASS = ""
PLAN_DIV_STYLE = f"font-size: 30px; font-weight: semibold;"

PLAN_PART_P_CLASS = ""
PLAN_PART_P_STYLE = f"font-weight: normal; font-size: 18px;"


def main_page(gui: Gui):
    wp = jp.WebPage(delete_flag = False)
    wp.page_type = 'main'
    wp.reload_interval = 1.0
    title_div = jp.Div(
        a=wp,
        classes=TITLE_DIV_CLASS,
        style=TITLE_DIV_STYLE,
    )
    fbk_logo_div = jp.Div(
        a=title_div,
        # text="FBK LOGO",
        # style="font-size: 30px;",
        style="height: 160px;",
    )
    fbk_logo = jp.Img(
        src="/static/logos/magazino-jh.png",
        a=fbk_logo_div,
        classes="w3-image",
        style="width: 400px",
        # style="height: 100%; length: auto;",
    )
    title_text_div = jp.Div(
        a=title_div,
        text="LOGISTICS AUTOMATION",
        style=TITLE_TEXT_DIV_STYLE,
    )
    unified_planning_logo_div = jp.Div(
        a=title_div,
        style="height: 160px;",
    )
    unified_planning = jp.Img(
        src="/static/logos/unified_planning_logo.png",
        a=unified_planning_logo_div,
        classes="w3-image",
        style="max-width: 100%; height: 160px;"
    )

    description_div = jp.Div(
        a=wp,
        style=DESCRIPTION_STYLE,
    )
    for single_desc in DESCRIPTION_TEXT.split("\n"):
        description_paragraph = jp.P(
            a=description_div,
            style=SINGLE_DESCRIPTION_STYLE,
            text=single_desc,
        )

    main_body_div = jp.Div(
        a=wp,
        classes=MAIN_BODY_DIV_CLASS,
        style=MAIN_BODY_DIV_STYLE,
    )

    actions_div = jp.Div(
        a=main_body_div,
        text="PROBLEM",
        classes=ACTIONS_DIV_CLASS,
        style=ACTIONS_DIV_STYLE,
    )

    # Useless paragprah, added just as a place-holder
    _ = jp.P(
        a=actions_div,
        text="",
    )

    gui.experiment_select = jp.Select(a=actions_div)
    gui.experiment_select.add(jp.Option(value="parallel_actions", text="Parallel actions"))
    gui.experiment_select.add(jp.Option(value="lost_capabilities", text="Lost capabilities"))
    gui.experiment_select.add(jp.Option(value="run_until_job", text="Wait until a job arrives"))
    gui.experiment_select.on("click", gui.update_steps_control)

    gui.step_select = jp.Select(a=actions_div)
    gui.step_select.on("click", gui.update_state_and_goal)

    # STATE AND GOAL SECTION
    gui.state_goal_div = jp.Div(
            a=main_body_div,
            text="STATE AND GOAL",
            classes=PLAN_DIV_CLASS,
            style=PLAN_DIV_STYLE,
        )
    solve = jp.Input(
        a=gui.state_goal_div,
        value="SOLVE",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    gui.state_div = jp.Div(
            a=gui.state_goal_div,
            text="Choose the experiment and the step to see the current state",
            classes=PLAN_PART_P_CLASS,
            style=PLAN_PART_P_STYLE,
    )
    solve.on('click', gui.solve_btn_click)

    gui.experiment_select.value = "parallel_actions"
    gui.update_steps_control(None)

    # PLAN SECTION
    gui.plan_div = jp.Div(
        a=main_body_div,
        text="PLAN",
        classes=PLAN_DIV_CLASS,
        style=PLAN_DIV_STYLE,
    )
    gui.update_planning_execution()

    return wp
