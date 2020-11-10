import workflowhub
from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.montage_recipe import MontageDataset
from workflowhub.generator import MontageRecipe

# creating a Seismology workflow recipe based on the number
# of pair of signals to estimate earthquake STFs
# recipe = MontageRecipe.from_num_tasks(num_tasks=133)
recipe = workflowhub.generator.workflow.montage_recipe.MontageRecipe(dataset=MontageDataset.DSS, num_bands=1, degree=0.5)

# creating an instance of the workflow generator with the
# Seismology workflow recipe
generator = WorkflowGenerator(recipe)

# generating a synthetic workflow trace of the Seismology workflow
workflow = generator.build_workflow()

# writing the synthetic workflow trace into a JSON file
workflow.write_json('montage-workflow.json')