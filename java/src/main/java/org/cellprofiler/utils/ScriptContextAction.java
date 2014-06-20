/**
 * CellProfiler is distributed under the GNU General Public License.
 * See the accompanying file LICENSE for details.
 *
 * Copyright (c) 2003-2009 Massachusetts Institute of Technology
 * Copyright (c) 2009-2014 Broad Institute
 * All rights reserved.
 * 
 * Please see the AUTHORS file for credits.
 * 
 * Website: http://www.cellprofiler.org
 */
package org.cellprofiler.utils;

import java.util.Map;
import java.util.concurrent.Callable;

import org.mozilla.javascript.Context;
import org.mozilla.javascript.ContextAction;
import org.mozilla.javascript.ContextFactory;
import org.mozilla.javascript.ImporterTopLevel;
import org.mozilla.javascript.Script;
import org.mozilla.javascript.Scriptable;
import org.mozilla.javascript.WrappedException;
import org.mozilla.javascript.Wrapper;

/**
 * @author Lee Kamentsky
 *
 * A javascript context action that runs a script
 * with optionally bound inputs and outputs.
 */
public class ScriptContextAction implements ContextAction {
	private final String script;
	private final Map<String, Object> inputBindings;
	private final Map<String, Object> outputBindings;
	private final ClassLoader applicationClassLoader;
	private WrappedException e;
	/**
	 * @param script script to execute
	 * @param inputBindings bindings of variable name to value
	 * @param outputBindings variable name to null to request
	 *        population of output bindings with the value
	 *        of the variable with the given name
	 * @param applicationClassLoader if supplied, the
	 *        application class loader to use when getting
	 *        classes.
	 */
	protected ScriptContextAction(
			String script,
			Map<String, Object> inputBindings,
			Map<String, Object> outputBindings,
			ClassLoader applicationClassLoader) {
		this.script = script;
		this.inputBindings = inputBindings;
		this.outputBindings = outputBindings;
		this.applicationClassLoader = applicationClassLoader;
	}
	/* (non-Javadoc)
	 * @see org.mozilla.javascript.ContextAction#run(org.mozilla.javascript.Context)
	 */
	public Object run(Context context) {
		try {
			if (applicationClassLoader != null) {
				context.setApplicationClassLoader(applicationClassLoader);
			}
			Script compiledScript = compileScript(context);
			final Scriptable scope = context.initStandardObjects();
			final Scriptable parentScope = new ImporterTopLevel(context);
			scope.setParentScope(parentScope);
			if (inputBindings != null) {
				for (Map.Entry<String, Object> entry:inputBindings.entrySet()) {
					scope.put(entry.getKey(), scope, entry.getValue());
				}
			}
			Object result = compiledScript.exec(context, scope);
			if (result instanceof Wrapper) {
				result = ((Wrapper)result).unwrap();
			}
			if (outputBindings != null) {
				for (Map.Entry<String, Object> entry:outputBindings.entrySet()) {
					entry.setValue(scope.get(entry.getKey(), scope));
				}
			}
			return result;
		} catch(WrappedException w) {
			this.e = w;
			return null;
		} catch (Throwable e) {
			this.e = new WrappedException(e);
			return null;
		}
	}
	
	private Script compileScript(Context context) {
		final Script result = context.compileString(script, "<java-python-bridge>", 1, null);
		return result;
	}
	/**
	 * Run a script
	 * @param script the javascript to run
	 * @param inputBindings a map of variable names to their values.
	 *        The script will run in a context where there are
	 *        variables with these names defined.
	 * @param outputBindings a map that, on input, consists
	 *        of variable names mapped to null. On output,
	 *        the map will contain the values of the named
	 *        variables.
	 * @param applicationClassLoader if not null, use this
	 *        class loader in the context of the script execution
	 * @return the value returned by the script.
	 */
	static public Object run(
			String script, 
			Map<String, Object> inputBindings,
			Map<String, Object> outputBindings,
			ClassLoader applicationClassLoader) {
		ScriptContextAction action = 
			new ScriptContextAction(
					script, inputBindings, 
					outputBindings, applicationClassLoader);
		final Object result = ContextFactory.getGlobal().call(action);
		if (action.e != null) throw action.e;
		return result;
	}
	
	/**
	 * Make a callable that, when executed, will run
	 * the javascript.
	 * @param script the javascript to run
	 * @param inputBindings a map of variable names to their values.
	 *        The script will run in a context where there are
	 *        variables with these names defined.
	 * @param outputBindings a map that, on input, consists
	 *        of variable names mapped to null. On output,
	 *        the map will contain the values of the named
	 *        variables.
	 * @param applicationClassLoader if not null, use this
	 *        class loader in the context of the script execution
	 * @return a callable wrapping the javascript execution
	 */
	static public Callable<Object> makeCallable(
			final String script,
			final Map<String, Object> inputBindings,
			final Map<String, Object> outputBindings,
			final ClassLoader applicationClassLoader) {
		return new Callable<Object> () {

			public Object call() throws Exception {
				return run(script, inputBindings, outputBindings, applicationClassLoader);
			}
			
		};
	}
	
	/**
	 * Make a runnable that, when executed, will run
	 * the javascript.
	 * @param script the javascript to run
	 * @param inputBindings a map of variable names to their values.
	 *        The script will run in a context where there are
	 *        variables with these names defined.
	 * @param outputBindings a map that, on input, consists
	 *        of variable names mapped to null. On output,
	 *        the map will contain the values of the named
	 *        variables.
	 * @param applicationClassLoader if not null, use this
	 *        class loader in the context of the script execution
	 * @return a Runnable wrapping the javascript execution
	 */
	static public Runnable makeRunnable(
			final String script,
			final Map<String, Object> inputBindings,
			final Map<String, Object> outputBindings,
			final ClassLoader applicationClassLoader) {
		return new Runnable () {

			public void run() {
				ScriptContextAction.run(script, inputBindings, outputBindings, applicationClassLoader);
			}
			
		};
	}
}
