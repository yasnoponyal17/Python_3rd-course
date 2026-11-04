import os
import random
from concurrent import futures
import grpc
import recommendations_pb2_grpc
from recommendations_pb2 import BookCategory, BookRecommendation, RecommendationResponse

BOOKS_BY_CATEGORY = {
    BookCategory.BOOK_CATEGORY_MYSTERY: [
        BookRecommendation(id=1, title="The Maltese Falcon"),
        BookRecommendation(id=2, title="Murder on the Orient Express"),
        BookRecommendation(id=3, title="The Hound of the Baskervilles"),
    ],
    BookCategory.BOOK_CATEGORY_SCIENCE_FICTION: [
        BookRecommendation(id=5, title="The Hitchhiker's Guide to the Galaxy"),
        BookRecommendation(id=6, title="Ender's Game"),
        BookRecommendation(id=7, title="Dune"),
    ],
}

class RecommendationService(recommendations_pb2_grpc.RecommendationsServicer):
    def Recommend(self, request, context):
        if request.max_results <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "max_results must be positive")
        if request.category == BookCategory.BOOK_CATEGORY_UNSPECIFIED:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "category is required")
            
        books = BOOKS_BY_CATEGORY.get(request.category)
        if books is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Category {request.category} not found")
            
        # Фильтрация прочитанных книг (Задание 3)
        excluded = set(request.exclude_ids)
        available_books = [b for b in books if b.id not in excluded]
        
        num_results = min(request.max_results, len(available_books))
        return RecommendationResponse(recommendations=random.sample(available_books, num_results))

def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(RecommendationService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Recommendations service listening on {port}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve(int(os.getenv("PORT", "50051")))