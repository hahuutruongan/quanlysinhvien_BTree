#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <algorithm>

using namespace std;

// ==========================================
// 1. CẤU TRÚC BẢNG DỮ LIỆU GỐC
// ==========================================
struct Student
{
    int rowId;
    char studentId[20];
    char name[100];
    char gender[10];
    bool isDeleted;
};

vector<Student> database;
int currentRowId = 0;

// ==========================================
// 2. CẤU TRÚC B-TREE 
// ==========================================
struct IndexKey
{
    string key;
    int rowId;
    IndexKey() : key(""), rowId(-1) {}
    IndexKey(string k, int id) : key(k), rowId(id) {}
};

class BTreeNode
{
public:
    IndexKey *keys;
    int t;
    BTreeNode **children;
    int numKeys;
    bool isLeaf;

    BTreeNode(int _t, bool _isLeaf)
    {
        t = _t;
        isLeaf = _isLeaf;
        keys = new IndexKey[2 * t - 1];
        children = new BTreeNode *[2 * t];
        numKeys = 0;
    }

    int search(string k);
    void insertNonFull(IndexKey k);
    void splitChild(int i, BTreeNode *y);
    void remove(string k);
    void removeFromLeaf(int idx);
    void removeFromNonLeaf(int idx);
    IndexKey getPred(int idx);
    IndexKey getSucc(int idx);
    void fill(int idx);
    void borrowFromPrev(int idx);
    void borrowFromNext(int idx);
    void merge(int idx);
};

class BTree
{
public:
    BTreeNode *root;
    int t;

    BTree(int _t)
    {
        root = nullptr;
        t = _t;
    }

    int search(string k)
    {
        return (root == nullptr) ? -1 : root->search(k);
    }

    void insert(string k, int rowId);
    void remove(string k);
};

// --- Triển khai các phương thức của BTreeNode ---

int BTreeNode::search(string k)
{
    int i = 0;
    while (i < numKeys && k > keys[i].key)
        i++;

    if (i < numKeys && keys[i].key == k)
        return keys[i].rowId;

    if (isLeaf)
        return -1;

    return children[i]->search(k);
}

void BTree::insert(string k, int rowId)
{
    IndexKey newKey(k, rowId);
    if (root == nullptr)
    {
        root = new BTreeNode(t, true);
        root->keys[0] = newKey;
        root->numKeys = 1;
    }
    else
    {
        if (root->numKeys == 2 * t - 1)
        {
            BTreeNode *s = new BTreeNode(t, false);
            s->children[0] = root;
            s->splitChild(0, root);

            int i = 0;
            if (s->keys[0].key < k)
                i++;
            s->children[i]->insertNonFull(newKey);

            root = s;
        }
        else
            root->insertNonFull(newKey);
    }
}

void BTreeNode::insertNonFull(IndexKey k)
{
    int i = numKeys - 1;

    if (isLeaf)
    {
        while (i >= 0 && keys[i].key > k.key)
        {
            keys[i + 1] = keys[i];
            i--;
        }
        keys[i + 1] = k;
        numKeys++;
    }
    else
    {
        while (i >= 0 && keys[i].key > k.key)
            i--;

        if (children[i + 1]->numKeys == 2 * t - 1)
        {
            splitChild(i + 1, children[i + 1]);
            if (keys[i + 1].key < k.key)
                i++;
        }
        children[i + 1]->insertNonFull(k);
    }
}

void BTreeNode::splitChild(int i, BTreeNode *y)
{
    BTreeNode *z = new BTreeNode(y->t, y->isLeaf);
    z->numKeys = t - 1;

    for (int j = 0; j < t - 1; j++)
        z->keys[j] = y->keys[j + t];

    if (!y->isLeaf)
    {
        for (int j = 0; j < t; j++)
            z->children[j] = y->children[j + t];
    }

    y->numKeys = t - 1;

    for (int j = numKeys; j >= i + 1; j--)
        children[j + 1] = children[j];

    children[i + 1] = z;

    for (int j = numKeys - 1; j >= i; j--)
        keys[j + 1] = keys[j];

    keys[i] = y->keys[t - 1];
    numKeys++;
}

void BTree::remove(string k)
{
    if (!root) return;

    root->remove(k);

    if (root->numKeys == 0)
    {
        BTreeNode *tmp = root;
        if (root->isLeaf)
            root = nullptr;
        else
            root = root->children[0];
        delete tmp;
    }
}

void BTreeNode::remove(string k)
{
    int idx = 0;
    while (idx < numKeys && keys[idx].key < k)
        idx++;

    if (idx < numKeys && keys[idx].key == k)
    {
        if (isLeaf)
            removeFromLeaf(idx);
        else
            removeFromNonLeaf(idx);
    }
    else
    {
        if (isLeaf) return;

        bool flag = (idx == numKeys);
        if (children[idx]->numKeys < t)
            fill(idx);

        if (flag && idx > numKeys)
            children[idx - 1]->remove(k);
        else
            children[idx]->remove(k);
    }
}

void BTreeNode::removeFromLeaf(int idx)
{
    for (int i = idx + 1; i < numKeys; i++)
        keys[i - 1] = keys[i];
    numKeys--;
}

void BTreeNode::removeFromNonLeaf(int idx)
{
    IndexKey k = keys[idx];

    if (children[idx]->numKeys >= t)
    {
        IndexKey pred = getPred(idx);
        keys[idx] = pred;
        children[idx]->remove(pred.key);
    }
    else if (children[idx + 1]->numKeys >= t)
    {
        IndexKey succ = getSucc(idx);
        keys[idx] = succ;
        children[idx + 1]->remove(succ.key);
    }
    else
    {
        merge(idx);
        children[idx]->remove(k.key);
    }
}

IndexKey BTreeNode::getPred(int idx)
{
    BTreeNode *cur = children[idx];
    while (!cur->isLeaf)
        cur = cur->children[cur->numKeys];
    return cur->keys[cur->numKeys - 1];
}

IndexKey BTreeNode::getSucc(int idx)
{
    BTreeNode *cur = children[idx + 1];
    while (!cur->isLeaf)
        cur = cur->children[0];
    return cur->keys[0];
}

void BTreeNode::fill(int idx)
{
    if (idx != 0 && children[idx - 1]->numKeys >= t)
        borrowFromPrev(idx);
    else if (idx != numKeys && children[idx + 1]->numKeys >= t)
        borrowFromNext(idx);
    else
    {
        if (idx != numKeys)
            merge(idx);
        else
            merge(idx - 1);
    }
}

void BTreeNode::borrowFromPrev(int idx)
{
    BTreeNode *child = children[idx];
    BTreeNode *sibling = children[idx - 1];

    for (int i = child->numKeys - 1; i >= 0; i--)
        child->keys[i + 1] = child->keys[i];

    if (!child->isLeaf)
    {
        for (int i = child->numKeys; i >= 0; i--)
            child->children[i + 1] = child->children[i];
    }

    child->keys[0] = keys[idx - 1];

    if (!child->isLeaf)
        child->children[0] = sibling->children[sibling->numKeys];

    keys[idx - 1] = sibling->keys[sibling->numKeys - 1];
    child->numKeys++;
    sibling->numKeys--;
}

void BTreeNode::borrowFromNext(int idx)
{
    BTreeNode *child = children[idx];
    BTreeNode *sibling = children[idx + 1];

    child->keys[child->numKeys] = keys[idx];

    if (!child->isLeaf)
        child->children[child->numKeys + 1] = sibling->children[0];

    keys[idx] = sibling->keys[0];

    for (int i = 1; i < sibling->numKeys; i++)
        sibling->keys[i - 1] = sibling->keys[i];

    if (!sibling->isLeaf)
    {
        for (int i = 1; i <= sibling->numKeys; i++)
            sibling->children[i - 1] = sibling->children[i];
    }

    child->numKeys++;
    sibling->numKeys--;
}

void BTreeNode::merge(int idx)
{
    BTreeNode *child = children[idx];
    BTreeNode *sibling = children[idx + 1];

    child->keys[t - 1] = keys[idx];

    for (int i = 0; i < sibling->numKeys; i++)
        child->keys[i + t] = sibling->keys[i];

    if (!child->isLeaf)
    {
        for (int i = 0; i <= sibling->numKeys; i++)
            child->children[i + t] = sibling->children[i];
    }

    for (int i = idx + 1; i < numKeys; i++)
        keys[i - 1] = keys[i];

    for (int i = idx + 2; i <= numKeys; i++)
        children[i - 1] = children[i];

    child->numKeys += sibling->numKeys + 1;
    numKeys--;
    delete sibling;
}

BTree indexById(2);
BTree indexByName(2);

string normalizeString(const char* str)
{
    string s(str);
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    return s;
}

// ==========================================
// 3. GIAO TIẾP C-API (CHO PYTHON GỌI)
// ==========================================
extern "C"
{
    int add_student(const char* id, const char* name, const char* gender, const char* norm_name) {
        int newRowId = currentRowId++;
        
        Student newStudent;
        newStudent.rowId = newRowId;
        strcpy(newStudent.studentId, id);
        strcpy(newStudent.name, name);
        strcpy(newStudent.gender, gender);
        newStudent.isDeleted = false;
        
        database.push_back(newStudent);

        indexById.insert(string(id), newRowId);
        indexByName.insert(string(norm_name), newRowId);

        return newRowId;
    }

    int search_by_id(const char* id)
    {
        return indexById.search(string(id));
    }

    int search_by_name(const char* norm_name)
    {
        return indexByName.search(string(norm_name));
    }

    void get_student_info(int rowId, char* out_id, char* out_name, char* out_gender)
    {
        if (rowId >= 0 && rowId < database.size() && !database[rowId].isDeleted)
        {
            strcpy(out_id, database[rowId].studentId);
            strcpy(out_name, database[rowId].name);
            strcpy(out_gender, database[rowId].gender);
        }
    }

    bool delete_student_by_id(const char* id)
    {
        int rowId = search_by_id(id);
        if (rowId != -1)
        {
            database[rowId].isDeleted = true;
            // Xóa cứng khỏi B-Tree Index
            indexById.remove(string(id));
            
            return true;
        }
        return false;
    }
}