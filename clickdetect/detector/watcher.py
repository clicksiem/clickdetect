from git import List
from .detector import Detector


class RuleWatcher:
    def __init__(self, detectors: List[Detector]):
        self.detectors = detectors
