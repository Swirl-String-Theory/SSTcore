#!/usr/bin/env node
'use strict';

// Legacy entry: knot embed alone is not a successful install.
// Delegate to the full native installer.
require('./install-native.js');
