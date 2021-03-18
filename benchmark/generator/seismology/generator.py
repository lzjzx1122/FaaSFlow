from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.seismology_recipe import SeismologyRecipe

num_tasks_list = [50, 100, 200, 500]
for task in num_tasks_list:
    print(task)
    recipe = SeismologyRecipe().from_num_tasks(num_tasks=task, output_file_size_factor=300)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '.json')
