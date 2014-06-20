package org.cellprofiler.utils;

import static org.junit.Assert.*;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

import org.junit.Test;
import org.mozilla.javascript.WrappedException;

public class TestScriptContextAction {

	@Test
	public void testHelloWorld() {
		assertEquals("Hello, world", ScriptContextAction.run(
				"'Hello, world';", null, null, null));
	}
	
	@Test
	public void testInputBinding() {
		Map<String, Object> inputBindings = new HashMap<String, Object>();
		inputBindings.put("you", "Fred");
		assertEquals("Hello, Fred", ScriptContextAction.run(
				"java.lang.String.format('Hello, %s', you)",
				inputBindings, null, null));
	}
	
	@Test
	public void testOutputBinding() {
		Map<String, Object> outputBindings = new HashMap<String, Object>();
		outputBindings.put("helloworld", null);
		ScriptContextAction.run(
				"var helloworld='Hello, output bindings'",
				null, outputBindings, null);
		assertEquals("Hello, output bindings", outputBindings.get("helloworld"));
	}
	@Test
	public void testException() {
		try {
			ScriptContextAction.run(
					"throw new java.lang.Exception('foo');",
					null, null, null);
			fail();
		} catch (WrappedException e) {
			assertTrue(e.getWrappedException() instanceof Exception);
			assertTrue(e.getWrappedException().getMessage().contains("foo"));
		}
	}
	@Test
	public void testBuiltIn() {
		final byte [] body = "Hello, world".getBytes();
		final String script = 
			"importPackage(java.security);\n"+
			"var md=MessageDigest.getInstance('SHA');\n"+
			"md.update(body);\n" +
			"md.toString();";
		final Map<String, Object> inputBindings = new HashMap<String, Object>();
		inputBindings.put("body", body);
		final Object result = ScriptContextAction.run(
				script, inputBindings, null, null);
		MessageDigest md;
		try {
			md = MessageDigest.getInstance("SHA");
		} catch (NoSuchAlgorithmException e) {
			fail();
			return;
		}
		md.update(body);
		assertEquals(md.toString(), result);
	}
	@Test
	public void testDoSomethingTwice() {
		String script = "java.lang.Double.valueOf('1.5')";
		ScriptContextAction.run(script, null, null, null);
		assertEquals(1.5, ScriptContextAction.run(script,  null,  null, null));
	}
	@Test
	public void testMakeCallable() {
		Object result;
		try {
			result = ScriptContextAction.makeCallable("'Hello, world'", null, null, null).call();
		} catch (Exception e) {
			fail();
			result = null;
		}
		assertEquals("Hello, world", result);		
	}
	@Test
	public void testMakeRunnable() {
		Map<String, Object> outputBindings = new HashMap<String, Object>();
		outputBindings.put("helloworld", null);
		ScriptContextAction.makeRunnable(
				"var helloworld='Hello, output bindings'",
				null, outputBindings, null).run();
		assertEquals("Hello, output bindings", outputBindings.get("helloworld"));
		
	}
}
