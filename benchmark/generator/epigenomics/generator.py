from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.epigenomics_recipe import EpigenomicsRecipe

num_tasks_list = [50, 100, 200, 500]
for task in num_tasks_list:
    print(task)
    recipe = EpigenomicsRecipe().from_num_tasks(num_tasks=task, runtime_factor=0.03, output_file_size_factor=0.03)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '.json')
