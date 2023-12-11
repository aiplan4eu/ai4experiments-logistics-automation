
import asyncio
from enum import Enum, auto


import logging
import queue
import justpy as jp
# FOR FUTURE PROJECTS: check out the justpy.react functionality: https://justpy.io/blog/reactivity/


import unified_planning as up
from unified_planning.shortcuts import *
from unified_planning.plot import plot_time_triggered_plan


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

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.logger.setLevel(logging.INFO)

    def reset_execution(self):
        self.mode = Mode.GENERATING_PROBLEM

    def update_planning_execution(self):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        if self.plan_div is not None:
            self.plan_div.delete_components()
            if self.plan is not None:
                _ = jp.P(
                    a=self.plan_div,
                    text=f"Found a plan!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
                for line in str(self.plan).split("\n"):
                     _ = jp.P(
                        a=self.plan_div,
                        text=line,
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
            elif self.plan_expected:
                if self.mode == Mode.GENERATING_PROBLEM:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="No plan found!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                else:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="Wait for planning to finish!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
            else:
                single_p = jp.P(
                    a=self.plan_div,
                    text="Plan will be displayed here!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
            try:
                asyncio.run(self.plan_div.update())
            except RuntimeError:
                self.plan_div.update()

    def clear_activities_click(self, msg):
        for jp_start_text in self.jp_components.values():
            jp_start_text.value = ""

    def show_gui_thread(self):
        from main_page import main_page
        @jp.SetRoute("/")
        def get_main_page():
            return main_page(self)
        jp.justpy(get_main_page)

    def generate_problem_click(self, msg):
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
                self.start_queue.put(None)
            else:
                self.logger.info("Invalid input")
                self.mode = Mode.GENERATING_PROBLEM
                self.input_values = {}
                self.components_disabled(False)

    def components_disabled(self, disabled: bool):
        return # TODO if needed
        for c1 in self.jp_components.values():
            c1.disabled = disabled

    def validate_input(self) -> bool:
        # self.input_values = {}
        # if self.jp_components is None:
        #     return False
        # for k, jp_start_text in self.jp_components.items():
        #     start_text = jp_start_text.value
        #     try:
        #         start_value = float(start_text)
        #     except ValueError:
        #         jp_start_text.value = "Err: NAN"
        #         return False
        #     if start_value < 1:
        #         jp_start_text.value = "Err: < 1"
        #         return False
        #     self.input_values[k] = start_value
        return True


def write_action_instance(action_instance: up.plans.ActionInstance) -> str:
    return str(action_instance)

async def reload_page():
    for page in jp.WebPage.instances.values():
        if page.page_type == 'main':
            await page.reload()
