from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.cycles_recipe import CyclesRecipe

recipe = CyclesRecipe()

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')