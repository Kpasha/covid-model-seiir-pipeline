from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, Tuple

from covid_model_seiir_pipeline.utilities import (
    Specification,
    asdict,
)
from covid_model_seiir_pipeline.workflow_tools.specification import (
    TaskSpecification,
    WorkflowSpecification,
)


class __PostprocessingJobs(NamedTuple):
    postprocess: str = 'postprocess'


POSTPROCESSING_JOBS = __PostprocessingJobs()


class PostprocessingTaskSpecification(TaskSpecification):
    """Specification of execution parameters for postprocessing tasks."""
    default_max_runtime_seconds = 15000
    default_m_mem_free = '150G'
    default_num_cores = 26


class PostprocessingWorkflowSpecification(WorkflowSpecification):
    """Specification of execution parameters for forecasting workflows."""

    tasks = {
        POSTPROCESSING_JOBS.postprocess: PostprocessingTaskSpecification,
    }


@dataclass
class PostprocessingData:
    """Specifies the inputs and outputs for postprocessing."""
    forecast_version: str = field(default='best')
    include_scenarios: list = field(default_factory=lambda: ['worse', 'reference', 'best_masks'])
    output_root: str = field(default='')

    def to_dict(self) -> Dict:
        """Converts to a dict, coercing list-like items to lists."""
        return asdict(self)


@dataclass
class SplicingSpecification:
    """Specifies locations and inputs for splicing."""
    locations: list = field(default_factory=list)
    output_version: str = field(default='')

    def to_dict(self) -> Dict:
        """Converts to a dict, coercing list-like items to lists."""
        return asdict(self)


@dataclass
class AggregationSpecification:
    """Specifies hierarchy and parameters for aggregation."""
    location_file: str = field(default='')
    location_set_id: int = field(default=None)
    location_set_version_id: int = field(default=None)

    def to_dict(self) -> Dict:
        """Converts to a dict, coercing list-like items to lists."""
        return asdict(self)


class PostprocessingSpecification(Specification):

    def __init__(self,
                 data: PostprocessingData,
                 splicing: List[SplicingSpecification],
                 aggregation: AggregationSpecification):
        self._data = data
        self._splicing = splicing
        self._aggregation = aggregation

    @classmethod
    def parse_spec_dict(cls, postprocessing_spec_dict: Dict) -> Tuple:
        """Construct postprocessing specification args from a dict."""
        data = PostprocessingData(**postprocessing_spec_dict.get('data', {}))
        splicing_configs = postprocessing_spec_dict.get('splicing', [])
        splicing = [SplicingSpecification(**splicing_config) for splicing_config in splicing_configs]
        aggregation = AggregationSpecification(**postprocessing_spec_dict.get('aggregation', {}))
        return data, splicing, aggregation

    @property
    def data(self) -> PostprocessingData:
        """The postprocessing data specification."""
        return self._data

    @property
    def splicing(self) -> List[SplicingSpecification]:
        return self._splicing

    @property
    def aggregation(self) -> AggregationSpecification:
        return self._aggregation

    def to_dict(self):
        """Convert the specification to a dict."""
        return {
            'data': self.data.to_dict(),
            'splicing': [splicing_config.to_dict() for splicing_config in self.splicing],
            'aggregation': self.aggregation.to_dict()
        }