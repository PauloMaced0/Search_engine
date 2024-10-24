import json
import math
import argparse
import os

def compute_dcg(relevances):
    """Compute DCG given a list of relevance scores."""
    dcg = 0.0
    for i, rel in enumerate(relevances):
        position = i + 1
        if position == 1:
            dcg += rel
        else:
            dcg += rel / math.log2(position)
    return dcg

def compute_idcg(relevances):
    """Compute IDCG by sorting the relevance scores in descending order."""
    sorted_relevances = sorted(relevances, reverse=True)
    return compute_dcg(sorted_relevances)

def compute_ndcg_at_k(retrieved_docs, gold_docs, k=10):
    """Compute nDCG@k for a single query."""
    relevances = []
    for doc_id in retrieved_docs[:k]:
        if doc_id in gold_docs:
            relevances.append(1)  # Relevant document
        else:
            relevances.append(0)  # Non-relevant document
    dcg = compute_dcg(relevances)
    idcg = compute_idcg(relevances)
    if idcg == 0:
        return 0.0
    return dcg / idcg

def compute_average_ndcg(questions_file_path, results_file_path, k=10):
    """Compute average nDCG@k over all queries."""
    # Load gold standard relevance judgements
    gold_data = {}
    with open(questions_file_path, 'r') as f:
        for line in f:
            question_data = json.loads(line)
            query_id = question_data['query_id']
            gold_docs = set(question_data['goldstandard_documents'])
            gold_data[query_id] = gold_docs

    # Load retrieved documents
    results_data = {}
    with open(results_file_path, 'r') as f:
        for line in f:
            result_entry = json.loads(line)
            query_id = result_entry['id']
            retrieved_docs = result_entry['retrieved_documents']
            results_data[query_id] = retrieved_docs

    # Compute nDCG@k for each query
    ndcg_scores = []
    for query_id, gold_docs in gold_data.items():
        retrieved_docs = results_data.get(query_id, [])
        ndcg = compute_ndcg_at_k(retrieved_docs, gold_docs, k)
        ndcg_scores.append(ndcg)
        print(f"Query ID: {query_id}, nDCG@{k}: {ndcg:.4f}")

    # Compute average nDCG@k
    average_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
    print(f"\nAverage nDCG@{k}: {average_ndcg:.4f}")
    return average_ndcg

def main():
    parser = argparse.ArgumentParser(description="Compute nDCG@10 for the retrieval system.")
    parser.add_argument('--questions_file', type=str, required=True, help="Path to the questions file (JSONL).")
    parser.add_argument('--results_file', type=str, required=True, help="Path to the ranked results file (JSONL).")
    parser.add_argument('--k', type=int, default=10, help="Rank cutoff for nDCG computation.")
    args = parser.parse_args()

    if not os.path.exists(args.questions_file):
        print(f"Questions file not found: {args.questions_file}")
        return
    if not os.path.exists(args.results_file):
        print(f"Results file not found: {args.results_file}")
        return

    compute_average_ndcg(args.questions_file, args.results_file, args.k)

if __name__ == '__main__':
    main()