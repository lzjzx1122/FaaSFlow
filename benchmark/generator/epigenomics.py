from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.epigenomics_recipe import EpigenomicsRecipe
from workflowhub.generator import EpigenomicsRecipe

# creating a Seismology workflow recipe based on the number
# of pair of signals to estimate earthquake STFs
# recipe = SeismologyRecipe.from_num_pairs(num_pairs=10)
# recipe = EpigenomicsRecipe.from_num_tasks(num_tasks=100)
recipe = EpigenomicsRecipe()

# creating an instance of the workflow generator with the
# Seismology workflow recipe
generator = WorkflowGenerator(recipe)

# generating a synthetic workflow trace of the Seismology workflow
workflow = generator.build_workflow()

# writing the synthetic workflow trace into a JSON file
workflow.write_json('epigenomics-workflow.json')