from sigma.processing.resolver import ProcessingPipelineResolver
resolver = ProcessingPipelineResolver()
pipelines = {
    name: pipe
    for name, pipe in resolver.list_pipelines()
}
print( 
      pipelines
)
