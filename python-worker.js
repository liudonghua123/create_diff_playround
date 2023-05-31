importScripts("pyodide/pyodide.js");

self.micropipIncludePre = false;
self.pythonModuleName = null;
self.initialized = false;
self.flet_js = {}; // namespace for Python global functions

self.initPyodide = async function () {
    self.pyodide = await loadPyodide();
    self.pyodide.registerJsModule("flet_js", flet_js);
    flet_js.documentUrl = documentUrl;
    await self.pyodide.loadPackage("micropip");
    let pre = self.micropipIncludePre ? "True" : "False";
    await self.pyodide.runPythonAsync(`
    import micropip
    import os
    from pyodide.http import pyfetch
    response = await pyfetch("app.tar.gz")
    await response.unpack_archive()
    # install patched flet-core package from custom url
    await micropip.install('pyodide/flet_core-0.7.4-py3-none-any.whl')
    await micropip.install('flet-pyodide')
  `);
    pyodide.pyimport(self.pythonModuleName);
    await self.flet_js.start_connection(self.receiveCallback);
    self.postMessage("initialized");
};

self.receiveCallback = (message) => {
    self.postMessage(message);
}

self.onmessage = async (event) => {
    // run only once
    if (!self.initialized) {
        self.initialized = true;
        self.documentUrl = event.data.documentUrl;
        self.micropipIncludePre = event.data.micropipIncludePre;
        self.pythonModuleName = event.data.pythonModuleName;
        await self.initPyodide();
    } else {
        // message
        flet_js.send(event.data);
    }
};