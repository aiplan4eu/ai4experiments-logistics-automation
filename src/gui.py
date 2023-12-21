import random
import asyncio
from enum import Enum, auto

from typing import Optional

import logging
import queue
import justpy as jp
# FOR FUTURE PROJECTS: check out the justpy.react functionality: https://justpy.io/blog/reactivity/

from experiment_definitions import experiments

import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.plot import plot_time_triggered_plan

from modified_planning import compute_plan

GRAPH_IMAGE_LOCATION = "/logos/generated/graph"
GRAPH_IMAGE_DIMENSIONS = "height: 100%; width: 100%;"

FIGSIZE = 16, 11


class Mode(Enum):
    GENERATING_PROBLEM = auto()
    OPERATING = auto()


class Gui():
    def __init__(self):
        # a queue where the interface waits the start
        self.start_queue = queue.Queue()

        self.mode = Mode.GENERATING_PROBLEM

        self.plan = None
        self.plan_expected: bool = False
        self.image_id = 0

        self.plan_div: Optional[jp.Div] = None
        self.graph_image_div: Optional[jp.Img] = None
        self.state_goal_div: Optional[jp.Div] = None
        self.state_div: Optional[jp.Div] = None
        self.experiment_select: Optional[jp.Select] = None
        self.step_select: Optional[jp.Select] = None

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.logger.setLevel(logging.INFO)
        self.logger.info("XXX")

    def reset_execution(self):
        self.mode = Mode.GENERATING_PROBLEM

    def update_state_and_goal(self, msg):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        state = experiments[self.experiment_select.value]["initial_state"]
        state = {**state, **experiments[self.experiment_select.value]["steps"][int(self.step_select.value)]["state_change"]}
        keyvals = [f"{key}: {val}" for key, val in state.items()]
        self.state_div.delete_components()
        self.state_div.text = ""
        jp.P(a=self.state_div, text=experiments[self.experiment_select.value]["steps"][int(self.step_select.value)]["description"], classes=PLAN_PART_P_CLASS, style=PLAN_PART_P_STYLE)
        p = jp.P(a=self.state_div, classes=PLAN_PART_P_CLASS, style=PLAN_PART_P_STYLE)
        p.inner_html = "&nbsp;"
        for keyval in keyvals:
            _ = jp.P(a=self.state_div, text=keyval, classes=PLAN_PART_P_CLASS, style=PLAN_PART_P_STYLE)

    def update_steps_control(self, msg):
        self.step_select.delete_components()
        if self.experiment_select.value in experiments:
            for s in range(0, len(experiments[self.experiment_select.value]["steps"])):
                self.step_select.add(jp.Option(value=str(s), text=f"Step {s}"))
        else:
            self.step_select.add(jp.Option(value="x", text="ERROR"))
        self.step_select.value = "0"
        self.update_state_and_goal(None)

    def show_plan(self):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        self.plan_div.delete_components()
        if self.plan is not None:
            _ = jp.P(
                a=self.plan_div,
                text=f"A plan has been found, the executor would execute the first operator in boldface (*__start or *__abort) or wait for an event (on_*). Move to the next step to see the new state.",
                classes=PLAN_PART_P_CLASS,
                style=PLAN_PART_P_STYLE,
            )
            p = jp.P(a=self.plan_div, classes=PLAN_PART_P_CLASS, style=PLAN_PART_P_STYLE)
            p.inner_html = "&nbsp;"
            for idx, line in enumerate(str(self.plan).split("\n")):
                if idx == 0:
                    continue
                p = jp.P(
                    a=self.plan_div,
                    text=line,
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
                if idx == 1:
                    p.inner_html = '<b>' + line + '</b>'

    def update_planning_execution(self):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        if self.plan_div is not None:
            self.plan_div.delete_components()
            if self.plan_expected:
                if self.mode == Mode.GENERATING_PROBLEM:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="No plan has been found!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                else:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="Wait for planning to finish...",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                    self.plan_div.update()
            else:
                _ = jp.P(
                    a=self.plan_div,
                    text="The plan will be displayed here.",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )

    def show_gui_thread(self):
        from main_page import main_page
        @jp.SetRoute("/")
        def get_main_page():
            return main_page(self)
        jp.justpy(get_main_page)

    def solve_btn_click(self, msg):
        self.logger.info("Generating")
        if self.mode == Mode.GENERATING_PROBLEM:
            self.mode = Mode.OPERATING
            self.components_disabled(True)
            if self.validate_input():
                self.logger.info("Valid input")
                self.plan = None
                self.plan_expected = True
                self.update_planning_execution()
                # unlock the planing method with the problem correctly generated
                #self.start_queue.put(None)
                self.plan = compute_plan(None, self)
                self.show_plan()
                self.reset_execution()
            else:
                self.logger.info("Invalid input")
                self.mode = Mode.GENERATING_PROBLEM
                self.input_values = {}
                self.components_disabled(False)

    def components_disabled(self, disabled: bool):
        return

    def validate_input(self) -> bool:
        return True


def write_action_instance(action_instance: up.plans.ActionInstance) -> str:
    return str(action_instance)


async def reload_page():
    for page in jp.WebPage.instances.values():
        if page.page_type == 'main':
            await page.reload()
