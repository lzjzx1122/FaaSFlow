from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.epigenomics_recipe import EpigenomicsRecipe

recipe = EpigenomicsRecipe()

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')