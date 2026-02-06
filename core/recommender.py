import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from django.utils import timezone
from datetime import timedelta
from .models import MyList

def count_old_mylist_entries():
    one_month_ago = timezone.now() - timedelta(days=30)
    return MyList.objects.filter(created_at__lt=one_month_ago, paid_status=False).count()

def cleanup_old_mylist_entries():
    one_month_ago = timezone.now() - timedelta(days=30)
    old_entries = MyList.objects.filter(created_at__lt=one_month_ago, paid_status=False)
    count = old_entries.count()
    old_entries.delete()

    return f"Deleted {count} old MyList entries."

def create_user_item_matrix(data):
    df = pd.DataFrame(data)
    # Apply weights: 2 for purchased items, 1 for items added to cart or wishlist but not purchased
    df['weight'] = df['paid_status'].apply(lambda x: 1.5 if x else 1)
    return df.pivot_table(index='user_id', columns='product_id', values='weight', aggfunc='max', fill_value=0)

def apply_svd(user_item_matrix, n_components=20):
    svd = TruncatedSVD(n_components=n_components)
    return svd.fit_transform(user_item_matrix)

def calculate_similarity(reduced_matrix):
    return cosine_similarity(reduced_matrix)

def recommend_products(user_id, user_similarity_matrix, user_item_matrix, product_data, top_n=5, similarity_threshold=0.4):
    user_similarity_df = pd.DataFrame(user_similarity_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)
    sim_scores = user_similarity_df[user_id].sort_values(ascending=False).drop(user_id)
    sim_scores = sim_scores[sim_scores > similarity_threshold]
    top_users = sim_scores.head(top_n).index

    if sim_scores.empty:
        print("No similar users found.")
        return []

    top_users_ratings = user_item_matrix.loc[top_users]
    weighted_ratings = top_users_ratings.multiply(sim_scores.loc[top_users], axis=0).sum(axis=0)

    print("Weighted ratings before category adjustments:", weighted_ratings)

    # Fetch user's previously interacted product categories
    previous_categories = MyList.objects.filter(user_id=user_id).values_list('product__category', flat=True).distinct()

    # Adjust weights for products in the same categories as previously interacted
    for product_id, weight in weighted_ratings.items():
        product_category = product_data.get(product_id, {}).get('category')
        if product_category in previous_categories:
            weighted_ratings[product_id] *= 1.5  # Increase weight by 50% if categories match
    
    print("Weighted ratings after category adjustments:", weighted_ratings)

    known_user_interactions = user_item_matrix.loc[user_id]
    filtered_recommendations = weighted_ratings[(known_user_interactions == 0) & (weighted_ratings > 0)]

    return filtered_recommendations.nlargest(top_n).index.values