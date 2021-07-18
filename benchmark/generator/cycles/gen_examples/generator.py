from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.cycles_recipe import CyclesRecipe

num_tasks_list = [400, 750, 900]
for task in num_tasks_list:
    print(task)
    recipe = CyclesRecipe().from_num_tasks(num_tasks=task, runtime_factor=0.1, output_file_size_factor=10)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '.json')
