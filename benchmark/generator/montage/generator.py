from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.montage_recipe import MontageRecipe
from workflowhub.generator.workflow.montage_recipe import MontageDataset

recipe = MontageRecipe(dataset=MontageDataset.DSS)

generator = WorkflowGenerator(recipe)

workflow = generator.build_workflow()

workflow.write_json('main.json')