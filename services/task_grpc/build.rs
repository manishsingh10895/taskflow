fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Use tonic_build to compile the protobuf files
    tonic_build::compile_protos("../../proto/task.proto")?;
    Ok(())
}
