
/**
 * @unit-test-setup
 * @ignore
 */
function setup() {
	global.Window = require('Window');
	global.WebView = require('WebView');
}

function baseline() {
}

/**
 * @see {Notification}
 * @example
 */
function run($utils) {
 	var $ = process.bridge.objc;

	var mainWindow = new Window();
	var webview = new WebView();
	mainWindow.appendChild(webview);
	mainWindow.addLayoutConstraint({
		priority:'required', relationship:'=',
		firstItem:webview, firstAttribute:'top',
		secondItem:mainWindow, secondAttribute:'top',
		multiplier:1.0, constant:0.0
	});
	mainWindow.addLayoutConstraint({
		priority:'required', relationship:'=',
		firstItem:webview, firstAttribute:'left',
		secondItem:mainWindow, secondAttribute:'left',
		multiplier:0.0, constant:0.0
	});
	mainWindow.addLayoutConstraint({
		priority:'required', relationship:'=',
		firstItem:webview, firstAttribute:'right',
		secondItem:mainWindow, secondAttribute:'right',
		multiplier:1.0, constant:0.0
	});
	mainWindow.addLayoutConstraint({
		priority:'required', relationship:'=',
		firstItem:webview, firstAttribute:'bottom',
		secondItem:mainWindow, secondAttribute:'bottom',
		multiplier:1.0, constant:0.0
	});
	webview.addEventListener('load', function() {
		mainWindow.title = webview.title;
		webview.postMessage('hello');
		/* @hidden */ webview.postMessage('hello2');
		/* @hidden */ webview.postMessage('hello3');
	});
	/* @hidden */ var count = 1;
	webview.addEventListener('title', function() {
		/* @hidden */ $utils.assert(webview.title == 'Test'+count);
		mainWindow.title = webview.title;
		/* @hidden */ if(count == 4) {
		/* @hidden */ 	mainWindow.close();
		/* @hidden */ 	$utils.ok();
		/* @hidden */ }
		/* @hidden */ count++;
	});
	webview.location = 'file://'+process.cwd()+'/assets/webview-test.html';

}

/**
 * @unit-test-shutdown
 * @ignore
 */
function shutdown() {
}

module.exports = {
	setup:setup, 
	run:run, 
	shutdown:shutdown, 
	shell:false,
	name:"WebView",
};