def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def chunk_markdown(lines):
    chunks = []
    current_chunk = []
    current_heading = ''

    for line in lines:
        if line.startswith('### '):
            if current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
            current_heading = line
            current_chunk.append(line)
        elif line.startswith('#### ') and len(''.join(current_chunk)) + len(line) > 1500:
            chunks.append(''.join(current_chunk))
            current_chunk = [f"({current_heading.strip()})\n", line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

def write_chunks_to_single_file(chunks, output_file_name):
    with open(output_file_name, 'w', encoding='utf-8') as file:
        for i, chunk in enumerate(chunks):
            file.write(f"--- Chunk {i} Start ---\n")
            file.write(chunk)
            file.write(f"\n--- Chunk {i} End ---\n\n")

def print_statistics(chunks):
    chunk_lengths = [(i, len(chunk)) for i, chunk in enumerate(chunks)]
    chunk_lengths.sort(key=lambda x: x[1], reverse=True)

    top_10_chunks = chunk_lengths[:10]
    largest_chunk = chunk_lengths[0]
    median_length = sorted([length for _, length in chunk_lengths])[len(chunk_lengths) // 2]
    mean_length = sum([length for _, length in chunk_lengths]) / len(chunk_lengths)

    print(f"Top 10 Largest Chunks (by characters): {top_10_chunks}")
    print(f"Largest Chunk (Chunk {largest_chunk[0]}): {largest_chunk[1]} characters")
    print(f"Content of the Largest Chunk:\n{chunks[largest_chunk[0]][:500]}...")  # Display first 500 characters
    print(f"Median Chunk Length: {median_length} characters")
    print(f"Mean Chunk Length: {mean_length:.2f} characters")

# Main process
file_path = "newMDfile.md"
lines = read_markdown(file_path)
chunks = chunk_markdown(lines)
write_chunks_to_single_file(chunks, "newMDfile_chunks.txt")
print_statistics(chunks)
