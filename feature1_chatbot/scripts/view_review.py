#!/usr/bin/env python3
# feature1_chatbot/scripts/view_review.py
import os, csv, argparse, sys

def view_csv(path, n=20):
    with open(path, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        for i,row in enumerate(r):
            print(row)
            if i+1 >= n:
                break

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--review", default="feature1_chatbot/review_queue.csv")
    p.add_argument("--n", type=int, default=30)
    args = p.parse_args()
    if not os.path.exists(args.review):
        print("Review file not found:", args.review)
        sys.exit(1)
    view_csv(args.review, n=args.n)

if __name__ == "__main__":
    main()
