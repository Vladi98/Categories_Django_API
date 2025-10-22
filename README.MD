# Category Tree Management API

A Django REST API for managing hierarchical category trees with bidirectional similarity relationships. Built with simplicity, maintainability, and performance in mind.

## 📋 Features

### Category Management
- **Hierarchical Tree Structure**: Unlimited nesting depth with parent-child relationships
- **Full CRUD Operations**: Create, read, update, and delete categories
- **Tree Operations**: Move categories, get ancestors/descendants, traverse the tree
- **Flexible Retrieval**: Query by parent, depth, search term, or get the entire tree
- **Image Support**: Upload and manage category images
- **Circular Reference Prevention**: Automatic validation to prevent tree corruption

### Similarity Management
- **Bidirectional Relationships**: Marking A similar to B automatically marks B similar to A
- **Efficient Storage**: Single database entry per similarity pair (normalized)
- **CRUD Operations**: Create, read, and delete similarity relationships
- **Bulk Operations**: Create multiple similarities in one request
- **Graph Analysis**: Find rabbit holes and rabbit islands

### Performance
- Optimized for up to **2,000 categories**

### How to run
- There is a **Makefile** containing all necessary commmands to build and start the API
- There is a **Sample data** prepared which populates the DB with records