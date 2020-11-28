from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.soykb_recipe import SoyKBRecipe

recipe = SoyKBRecipe()

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')