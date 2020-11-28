from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.seismology_recipe import SeismologyRecipe

recipe = SeismologyRecipe()

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')