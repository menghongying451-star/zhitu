from .agents.tianbao import TianBaoAgent
from .agents.wenshi import WenShiAgent
from .agents.zhitu import ZhiTuAgent

AGENTS = {a.name: a for a in (WenShiAgent(), ZhiTuAgent(), TianBaoAgent())}


def get_agent(name: str):
    return AGENTS.get(name)
