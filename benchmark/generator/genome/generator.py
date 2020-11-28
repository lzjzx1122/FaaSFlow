from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.genome_recipe import GenomeRecipe

recipe = GenomeRecipe()

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')