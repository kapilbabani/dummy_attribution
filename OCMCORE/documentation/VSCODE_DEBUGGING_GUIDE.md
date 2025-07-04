# VS Code Debugging Guide

## 🎯 Overview

This guide explains how to debug your Django applications directly within VS Code using the integrated debugging features. VS Code provides powerful debugging capabilities including breakpoints, variable inspection, call stack analysis, and more.

## 🚀 Quick Start

### 1. Open Your Project in VS Code
```bash
# Navigate to your project
cd OCMCORE

# Open VS Code
code .
```

### 2. Set Breakpoints
- Click in the left margin of any Python file to set a breakpoint
- Breakpoints appear as red dots
- You can set multiple breakpoints across different files

### 3. Start Debugging
- Press **F5** or go to **Run and Debug** (Ctrl+Shift+D)
- Select a debug configuration from the dropdown
- Click the green play button or press F5

## 🔧 Debug Configurations

The project includes several pre-configured debug configurations in `.vscode/launch.json`:

### **Django Debug**
- **Purpose**: Normal debugging with cache support
- **Use case**: General development and debugging
- **Features**: Full Django debugging with Memcached

### **Django Debug (No Cache)**
- **Purpose**: Debugging without cache interference
- **Use case**: When cache is causing issues or you want to test without caching
- **Features**: Django debugging with cache disabled

### **Django Debug (Verbose)**
- **Purpose**: Debugging with detailed Django output
- **Use case**: When you need to see all Django operations
- **Features**: Verbose logging and detailed error messages

### **Test Memcached**
- **Purpose**: Debug Memcached connection and operations
- **Use case**: Testing cache functionality
- **Features**: Debug the Memcached test script

### **Test Pattern Cache**
- **Purpose**: Debug pattern-based cache operations
- **Use case**: Testing cache pattern matching functionality
- **Features**: Debug the cache pattern test script

## 🎯 Debugging Workflow

### Step 1: Prepare Your Environment
```bash
# Ensure your virtual environment is set up
# The debug configuration automatically uses: ./venv/Scripts/python.exe

# Start Memcached if needed (for cache-enabled debugging)
docker-compose -f docker-compose.dev.yml up -d memcached
```

### Step 2: Set Breakpoints
1. Open the file you want to debug (e.g., `attribution/views.py`)
2. Click in the left margin next to the line number where you want to pause execution
3. A red dot will appear indicating a breakpoint

**Example breakpoint locations:**
```python
# In attribution/views.py
class GenerateAttribution(APIView):
    def post(self, request):
        # Set breakpoint here to inspect request data
        beg_date = request.data.get('beg_date')  # ← Breakpoint here
        end_date = request.data.get('end_date')
        
        # Set breakpoint here to inspect processed data
        result = generate_attribution_service(beg_date, end_date, id1, id2, attributes)  # ← Breakpoint here
        return Response(result)
```

### Step 3: Start Debugging
1. Press **F5** or go to **Run and Debug** (Ctrl+Shift+D)
2. Select **"Django Debug"** from the dropdown
3. Click the green play button
4. VS Code will start the Django development server in debug mode

### Step 4: Trigger the Code
1. Make a request to your API endpoint (e.g., using Postman, curl, or browser)
2. When the code reaches a breakpoint, execution will pause
3. VS Code will show the debugging interface

### Step 5: Inspect and Debug
When paused at a breakpoint, you can:

#### **Variables Panel**
- View all local variables and their values
- Expand objects to see their properties
- Hover over variables in the code to see their values

#### **Call Stack**
- See the execution path that led to the current breakpoint
- Click on different stack frames to inspect variables at each level

#### **Watch Expressions**
- Add specific variables or expressions to monitor
- Right-click on variables and select "Add to Watch"

#### **Debug Console**
- Execute Python code in the current context
- Test expressions and inspect objects

## 🔧 Debug Controls

### **Step Controls**
- **Continue (F5)**: Resume execution until the next breakpoint
- **Step Over (F10)**: Execute the current line and move to the next line
- **Step Into (F11)**: Step into function calls
- **Step Out (Shift+F11)**: Step out of the current function
- **Restart (Ctrl+Shift+F5)**: Restart the debugging session
- **Stop (Shift+F5)**: Stop debugging

### **Breakpoint Management**
- **Toggle Breakpoint (F9)**: Add/remove breakpoint at current line
- **Enable/Disable Breakpoint**: Right-click breakpoint to enable/disable
- **Conditional Breakpoints**: Right-click breakpoint to add conditions

## 🎯 Common Debugging Scenarios

### **Debugging API Requests**

1. **Set breakpoint in your view:**
```python
# In your app's views.py
class YourView(APIView):
    def post(self, request):
        # Set breakpoint here
        data = request.data  # ← Breakpoint here
        result = process_data(data)
        return Response(result)
```

2. **Start debugging and make a request:**
```bash
# In another terminal or Postman
curl -X POST http://localhost:8000/api/your-endpoint/ \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

3. **Inspect the request data in VS Code**

### **Debugging Database Operations**

1. **Set breakpoint in your service:**
```python
# In your app's services.py
def your_service_function():
    # Set breakpoint here
    queryset = YourModel.objects.filter(is_active=True)  # ← Breakpoint here
    return list(queryset.values())
```

2. **Inspect the queryset and results**

### **Debugging Cache Operations**

1. **Set breakpoint in cache-related code:**
```python
# In your service
from simple_cache import simple_cache

def cached_function():
    # Set breakpoint here
    cache_key = "my_cache_key"  # ← Breakpoint here
    cached_data = simple_cache.get(cache_key)
    
    if cached_data:
        return cached_data  # ← Breakpoint here
    
    # Generate new data
    new_data = expensive_operation()
    simple_cache.set(cache_key, new_data, timeout=3600)
    return new_data
```

2. **Inspect cache keys and data**

## 🔍 Advanced Debugging Features

### **Conditional Breakpoints**
Right-click on a breakpoint and select "Edit Breakpoint" to add conditions:

```python
# Example: Only break when user_id is 123
user_id == 123

# Example: Only break when data is empty
len(data) == 0

# Example: Only break on specific error
'error' in str(e).lower()
```

### **Logpoints**
Instead of breaking execution, logpoints print messages to the debug console:

1. Right-click in the margin and select "Add Logpoint"
2. Enter your log message: `"Processing user: {user_id}"`
3. Execution continues but logs the message

### **Exception Breakpoints**
Automatically break when exceptions occur:

1. Go to **Run and Debug** panel
2. Click on **Breakpoints** section
3. Check **"Uncaught Exceptions"** or **"Raised Exceptions"**

### **Watch Expressions**
Monitor specific variables or expressions:

1. In the **Watch** panel, click the **+** button
2. Enter an expression: `request.data.get('user_id')`
3. The expression will be evaluated at each breakpoint

## 🚨 Troubleshooting

### **Debugger Not Starting**
- **Issue**: "Python interpreter not found"
- **Solution**: Ensure your virtual environment is properly set up
- **Check**: `.vscode/settings.json` has correct Python path

### **Breakpoints Not Hitting**
- **Issue**: Breakpoints appear hollow (not filled)
- **Solution**: Check that the file path in VS Code matches the actual file
- **Check**: Ensure you're running the correct debug configuration

### **Import Errors**
- **Issue**: Module import errors during debugging
- **Solution**: Ensure all dependencies are installed in your virtual environment
- **Check**: Run `pip install -r requirements.txt`

### **Django Not Starting**
- **Issue**: Django server fails to start in debug mode
- **Solution**: Check environment variables and database connection
- **Check**: Ensure `.env` file is properly configured

### **Cache Connection Issues**
- **Issue**: Memcached connection errors
- **Solution**: Start Memcached container before debugging
- **Command**: `docker-compose -f docker-compose.dev.yml up -d memcached`

## 🎯 Best Practices

### **1. Use Descriptive Breakpoints**
- Set breakpoints at logical points in your code
- Use conditional breakpoints to focus on specific scenarios
- Remove breakpoints when no longer needed

### **2. Leverage the Debug Console**
- Test expressions and inspect objects
- Execute code in the current context
- Use it to understand variable values

### **3. Use Watch Expressions**
- Monitor important variables throughout debugging
- Add complex expressions to watch
- Use watch expressions for temporary debugging

### **4. Organize Your Debugging**
- Use different debug configurations for different scenarios
- Keep related breakpoints together
- Document debugging steps for complex issues

### **5. Clean Up After Debugging**
- Remove unnecessary breakpoints
- Clear watch expressions
- Stop debugging sessions when done

## 🔧 Configuration Files

### **`.vscode/launch.json`**
Contains all debug configurations with environment variables and settings.

### **`.vscode/settings.json`**
Contains VS Code workspace settings for Python, linting, and file management.

## 🎯 Example Debugging Session

### **Scenario**: Debugging an API endpoint that's returning incorrect data

1. **Set breakpoints:**
```python
# In your view
def post(self, request):
    data = request.data  # ← Breakpoint 1
    processed_data = self.process_data(data)  # ← Breakpoint 2
    return Response(processed_data)

def process_data(self, data):
    result = {}  # ← Breakpoint 3
    for key, value in data.items():
        result[key] = self.transform_value(value)  # ← Breakpoint 4
    return result
```

2. **Start debugging** with "Django Debug" configuration

3. **Make a request** to your endpoint

4. **Inspect at each breakpoint:**
   - Breakpoint 1: Check `request.data`
   - Breakpoint 2: Check `processed_data`
   - Breakpoint 3: Check `result` initialization
   - Breakpoint 4: Check `value` transformation

5. **Use debug console** to test expressions and inspect objects

6. **Step through code** to understand the execution flow

## 🎉 Summary

VS Code debugging provides powerful tools for understanding and fixing issues in your Django applications. With proper setup and practice, you can efficiently debug complex problems and understand your code's behavior in detail.

**Key Benefits:**
- ✅ Interactive debugging with breakpoints
- ✅ Variable inspection and watch expressions
- ✅ Call stack analysis
- ✅ Debug console for testing
- ✅ Integration with Django development server
- ✅ Support for all project configurations 