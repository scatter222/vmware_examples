import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('myAuthView', new MyAuthViewProvider(context))
    );
}



class MyAuthViewProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(private readonly context: vscode.ExtensionContext) {}

    resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        // Set up the webview content
        webviewView.webview.options = {
            enableScripts: true,
        };

        // Check if user is authenticated (just an example, replace with your logic)
        const isAuthenticated = this.context.workspaceState.get<boolean>('authenticated', false);

        // Generate content
        webviewView.webview.html = this.getHtmlContent(isAuthenticated);

        // Handle button click message from webview
        webviewView.webview.onDidReceiveMessage((message) => {
            if (message.command === 'authenticate') {
                // Handle authentication
                vscode.window.showInformationMessage('Authentication started...');
                // Example logic for setting authentication state
                this.context.workspaceState.update('authenticated', true);
                webviewView.webview.html = this.getHtmlContent(true);
            }
        });
    }


    
    private getHtmlContent(isAuthenticated: boolean): string {
        if (!isAuthenticated) {
            // Show a button in the middle of the view
            return `
                <html>
                <body style="display: flex; align-items: center; justify-content: center; height: 100%;">
                    <button onclick="authenticate()">Click to Authenticate</button>
                    <script>
                        const vscode = acquireVsCodeApi();
                        function authenticate() {
                            vscode.postMessage({ command: 'authenticate' });
                        }
                    </script>
                </body>
                </html>`;
        } else {
            return `
                <html>
                <body>
                    <h3>You are authenticated</h3>
                </body>
                </html>`;
        }
    }
}
