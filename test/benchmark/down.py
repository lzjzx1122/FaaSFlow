import repository
import pandas as pd

repo = repository.Repository()
latency = repo.down_latency()
df = pd.DataFrame({'latency': latency})
df.to_csv('1.csv', index=False)