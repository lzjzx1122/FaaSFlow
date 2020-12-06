from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.epigenomics_recipe import EpigenomicsRecipe

recipe = EpigenomicsRecipe(num_sequence_files = 1, num_lines = 40)

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')