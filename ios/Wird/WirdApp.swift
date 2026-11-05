// «وِرد» للآيفون: غلاف أصلي بسيط يعرض نفس تطبيق الويب (apps/wird) من داخل الحزمة، بلا إنترنت.
// الملفات تُخدَم عبر wird://app/ لتبقى بيانات localStorage محفوظة بين مرات التشغيل.
import UIKit
import WebKit
import UniformTypeIdentifiers

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = WebController()
        window?.makeKeyAndVisible()
        return true
    }
}

final class BundleScheme: NSObject, WKURLSchemeHandler {
    let root = Bundle.main.resourceURL!.appendingPathComponent("web")
    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        var path = task.request.url?.path ?? "/"
        if path == "/" || path.isEmpty { path = "/index.html" }
        let file = root.appendingPathComponent(String(path.dropFirst())).standardizedFileURL
        guard file.path.hasPrefix(root.standardizedFileURL.path), let data = try? Data(contentsOf: file) else {
            task.didReceive(HTTPURLResponse(url: task.request.url!, statusCode: 404, httpVersion: "HTTP/1.1", headerFields: [:])!)
            task.didFinish(); return
        }
        let mime = UTType(filenameExtension: file.pathExtension)?.preferredMIMEType ?? "application/octet-stream"
        let res = HTTPURLResponse(url: task.request.url!, statusCode: 200, httpVersion: "HTTP/1.1",
                                  headerFields: ["Content-Type": mime, "Content-Length": String(data.count)])!
        task.didReceive(res); task.didReceive(data); task.didFinish()
    }
    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

final class WebController: UIViewController, WKUIDelegate {
    var web: WKWebView!
    override func loadView() {
        let cfg = WKWebViewConfiguration()
        cfg.setURLSchemeHandler(BundleScheme(), forURLScheme: "wird")
        cfg.websiteDataStore = .default()
        cfg.allowsInlineMediaPlayback = true
        cfg.mediaTypesRequiringUserActionForPlayback = []
        web = WKWebView(frame: .zero, configuration: cfg)
        web.uiDelegate = self
        web.isOpaque = false
        web.backgroundColor = UIColor(red: 0.91, green: 0.95, blue: 0.98, alpha: 1)
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.scrollView.bounces = false
        web.allowsBackForwardNavigationGestures = false
        view = web
    }
    override func viewDidLoad() {
        super.viewDidLoad()
        UIApplication.shared.isIdleTimerDisabled = false
        web.load(URLRequest(url: URL(string: "wird://app/index.html")!))
    }
    override var prefersHomeIndicatorAutoHidden: Bool { false }
    // confirm()/alert()/prompt() من التطبيق تظهر كنوافذ iOS عادية
    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: m, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "حسنًا", style: .default) { _ in done() }); present(a, animated: true)
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping (Bool) -> Void) {
        let a = UIAlertController(title: nil, message: m, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "إلغاء", style: .cancel) { _ in done(false) })
        a.addAction(UIAlertAction(title: "موافق", style: .default) { _ in done(true) }); present(a, animated: true)
    }
    func webView(_ w: WKWebView, runJavaScriptTextInputPanelWithPrompt p: String, defaultText t: String?, initiatedByFrame f: WKFrameInfo, completionHandler done: @escaping (String?) -> Void) {
        let a = UIAlertController(title: nil, message: p, preferredStyle: .alert)
        a.addTextField { $0.text = t }
        a.addAction(UIAlertAction(title: "إلغاء", style: .cancel) { _ in done(nil) })
        a.addAction(UIAlertAction(title: "موافق", style: .default) { _ in done(a.textFields?.first?.text) }); present(a, animated: true)
    }
}
