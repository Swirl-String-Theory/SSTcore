# Dashboard / Angular bridge (optional)

The **browser** does not load `.node` binaries. For an Angular (or similar) UI, run a **small Node backend** (Nest, Express, etc.) that `require('SSTcore')` and exposes HTTP routes.

**Contract:** treat `node_examples/*.example.ts` as the reference for request bodies and response shapes. Each example file matches one `src/node/node_*.cpp` binding module; backend handlers can wrap the same calls the examples use.

See also [ANGULAR_API.md](./ANGULAR_API.md) and root `index.d.ts` for the TypeScript surface.
