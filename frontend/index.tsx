import { injectProtonDB } from '../webkit/protondb';

export default async function PluginMain(): Promise<void> {
  injectProtonDB();
}
