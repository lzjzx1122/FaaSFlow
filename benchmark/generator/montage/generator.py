from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.montage_recipe import MontageRecipe
from workflowhub.generator.workflow.montage_recipe import MontageDataset

num_tasks_list = [500, 700]
for task in num_tasks_list:
    print(task)
    recipe = MontageRecipe().from_num_tasks(num_tasks=task, runtime_factor=0.04, output_file_size_factor=0.04)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '.json')
