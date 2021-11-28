from workflowhub import WorkflowGenerator
from workflowhub.generator.workflow.genome_recipe import GenomeRecipe

num_tasks_list = [25,50,200]
for task in num_tasks_list:
    print(task)
    recipe = GenomeRecipe().from_num_tasks(num_tasks=task, runtime_factor=0.05, input_file_size_factor=0.003, output_file_size_factor=10)
    generator = WorkflowGenerator(recipe)
    workflow = generator.build_workflow()
    workflow.write_json('main_' + str(task) + '.json')
